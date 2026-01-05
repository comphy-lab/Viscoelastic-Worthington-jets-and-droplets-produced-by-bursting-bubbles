@include <sys/mman.h>

// macOS compatibility: Explicitly define missing constants and function declarations
#ifdef __APPLE__
# ifndef MAP_ANON
#  define MAP_ANON 0x1000
# endif
# ifndef MAP_ANONYMOUS
#  define MAP_ANONYMOUS MAP_ANON
# endif
# ifndef POSIX_MADV_DONTNEED
#  define POSIX_MADV_DONTNEED 4
# endif
# ifndef MADV_DONTNEED
#  define MADV_DONTNEED POSIX_MADV_DONTNEED
# endif
// Ensure madvise() is declared
int madvise(void *, size_t, int);
#endif
