#!/bin/bash
# parse_params.sh - Shell library for parameter file parsing
# Source this file: source src-local/parse_params.sh

# Parse a parameter file and export all parameters as environment variables
# Usage: parse_param_file <file>
parse_param_file() {
    local param_file=$1

    if [ ! -f "$param_file" ]; then
        echo "ERROR: Parameter file $param_file not found" >&2
        return 1
    fi

    # Read parameters (skip comments and empty lines)
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue

        # Remove inline comments and whitespace
        value=$(echo "$value" | sed 's/#.*//' | xargs)
        key=$(echo "$key" | xargs)

        # Skip if key or value is empty
        [ -z "$key" ] && continue
        [ -z "$value" ] && continue

        # Export as environment variable with PARAM_ prefix
        export "PARAM_${key}=${value}"
    done < "$param_file"

    return 0
}

# Get a parameter value with optional default
# Usage: get_param <key> [default]
get_param() {
    local key=$1
    local default=${2:-}
    local var_name="PARAM_${key}"
    echo "${!var_name:-$default}"
}

# Generate sweep combinations and create parameter files
# Usage: generate_sweep_cases <sweep_file>
# Returns: directory containing generated parameter files
generate_sweep_cases() {
    local sweep_file=$1

    if [ ! -f "$sweep_file" ]; then
        echo "ERROR: Sweep file $sweep_file not found" >&2
        return 1
    fi

    # Source the sweep file to get variables
    source "$sweep_file"

    # Check if BASE_CONFIG is defined
    if [ -z "$BASE_CONFIG" ]; then
        echo "ERROR: BASE_CONFIG not defined in sweep file" >&2
        return 1
    fi

    # Parse base configuration
    parse_param_file "$BASE_CONFIG"

    # Create temporary directory for generated cases
    local temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/sweep.XXXXXX")

    # Extract sweep variables
    local sweep_vars=()
    local sweep_values=()

    while IFS='=' read -r line; do
        # Remove comments
        line=$(echo "$line" | sed 's/#.*//')
        [ -z "$line" ] && continue

        # Match SWEEP_* variables
        if [[ "$line" =~ ^[[:space:]]*SWEEP_([^=]+)=(.+)$ ]]; then
            var_name="${BASH_REMATCH[1]}"
            var_values="${BASH_REMATCH[2]}"
            sweep_vars+=("$var_name")
            sweep_values+=("$var_values")
        fi
    done < "$sweep_file"

    if [ ${#sweep_vars[@]} -eq 0 ]; then
        echo "ERROR: No SWEEP_* variables found in $sweep_file" >&2
        rm -rf "$temp_dir"
        return 1
    fi

    # Generate cartesian product of sweep values
    local case_num=0

    # Recursive function to generate all combinations
    generate_recursive() {
        local depth=$1
        shift
        local current_values=("$@")

        if [ $depth -eq ${#sweep_vars[@]} ]; then
            # Base case: all variables assigned, create parameter file
            local case_file="${temp_dir}/case_$(printf "%04d" $case_num).params"
            local output_dir="$OUTPUT_TEMPLATE"

            # Copy base config
            cp "$BASE_CONFIG" "$case_file"

            # Override with sweep values
            for i in "${!sweep_vars[@]}"; do
                local var="${sweep_vars[$i]}"
                local val="${current_values[$i]}"

                # Replace in parameter file
                if grep -q "^${var}=" "$case_file"; then
                    sed -i.bak "s|^${var}=.*|${var}=${val}|" "$case_file"
                else
                    echo "${var}=${val}" >> "$case_file"
                fi
                rm -f "${case_file}.bak"

                # Replace in output template
                output_dir="${output_dir//\{${var}\}/${val}}"
            done

            # Set output directory
            if grep -q "^output_dir=" "$case_file"; then
                sed -i.bak "s|^output_dir=.*|output_dir=${output_dir}|" "$case_file"
            else
                echo "output_dir=${output_dir}" >> "$case_file"
            fi
            rm -f "${case_file}.bak"

            ((case_num++))
            return
        fi

        # Recursive case: iterate through values for current variable
        local values="${sweep_values[$depth]}"
        IFS=',' read -ra value_array <<< "$values"

        for val in "${value_array[@]}"; do
            val=$(echo "$val" | xargs)  # Trim whitespace
            generate_recursive $((depth + 1)) "${current_values[@]}" "$val"
        done
    }

    # Start recursion
    generate_recursive 0

    echo "$temp_dir"
    return 0
}

# Validate that required variables are set in parameter file
# Usage: validate_required_params <param1> <param2> ...
validate_required_params() {
    local missing=0

    for param in "$@"; do
        local var_name="PARAM_${param}"
        if [ -z "${!var_name}" ]; then
            echo "ERROR: Required parameter '$param' not found" >&2
            missing=1
        fi
    done

    return $missing
}

# Print all loaded parameters (for debugging)
print_params() {
    echo "Loaded parameters:"
    env | grep "^PARAM_" | sort | while IFS='=' read -r key value; do
        key="${key#PARAM_}"
        echo "  $key = $value"
    done
}
