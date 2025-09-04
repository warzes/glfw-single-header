# forked from https://github.com/SasLuca/glfw-single-header (CC0-1.0 licensed)
# _GLFW_COCOA
# _GLFW_WIN32
# _GLFW_X11
# _GLFW_WAYLAND
# _GLFW_OSMESA

import os

win32_defines = [ 
                 "#define _UNICODE",
                 "#ifdef MINGW\n#define UNICODE\n#define WINVER 0x0501\n#endif",
                ]

win32_sources   = [ "win32_init.c", "win32_joystick.c", "win32_module.c", "win32_monitor.c", "win32_time.c", "win32_thread.c", "win32_window.c", "wgl_context.c", ]
osmesa_sources  = [ "null_init.c", "null_monitor.c", "null_window.c", "null_joystick.c", ]
x11_sources     = [ "x11_init.c", "x11_monitor.c", "x11_window.c", "glx_context.c",  ]
wayland_sources = [ "wl_init.c", "wl_monitor.c", "wl_window.c",  ]
cocoa_sources   = [ "cocoa_init.m", "nsgl_context.m", "cocoa_joystick.m", "cocoa_monitor.m", "cocoa_window.m", "cocoa_time.c", ]
time_sources    = [ "posix_time.c", ]
thread_sources  = [ "posix_thread.c", ]
module_sources  = [ "posix_module.c", ]
poll_sources  = [ "posix_poll.c", ]

linux_sources   = [ "linux_joystick.c", "xkb_unicode.c", ]

headers = list([
"cocoa_joystick.h",
"cocoa_platform.h",
"cocoa_time.h",
"egl_context.h",
"glx_context.h",
"linux_joystick.h",
"mappings.h",
"nsgl_context.h",
"null_joystick.h",
"null_platform.h",
"platform.h",
"osmesa_context.h",
"posix_poll.h",
"posix_thread.h",
"posix_time.h",
"wgl_context.h",
"win32_joystick.h",
"win32_platform.h",
"win32_thread.h",
"win32_time.h",
"wl_platform.h",
"x11_platform.h",
"xkb_unicode.h",
])
shared_sources = [ "internal.h", "osmesa_context.c", "egl_context.c", "context.c", "init.c", "input.c", "platform.c", "monitor.c", "vulkan.c", "window.c", ]

# Get the file using this function since it might be cached
files_cache = {}
def lsh_get_file(it: str) -> str:
    global files_cache
    if it in files_cache.keys():
        return files_cache[it]

    guard = f"HEADER_GUARD_{it.replace('.', '_').upper()}"
    code = open(f"./glfw/src/{it}").read()
    files_cache[it] = f"\n//#line 1 \"{it}\"\n"
    files_cache[it]+= f"\n#ifndef {guard}\n#define {guard}\n{code}\n#endif\n"

    return files_cache[it]

# Include the headers into a source
def include_headers(headers, source: str) -> str:
    if len(headers) == 0:
        return source

    for it in headers:
        if source.find(f"#include \"{it}\"") != -1:
            h = include_headers([i for i in headers if i != it], lsh_get_file(it))
            source = source.replace(f"#include \"{it}\"", f"\n{h}\n")
    return source

# Add shared code
shared_source_result = ""
for it in shared_sources:
    shared_source_result += include_headers(headers, lsh_get_file(it))

# Add win32 code
win32_source_result = "\n#ifdef _GLFW_WIN32\n"
for it in win32_defines:
    win32_source_result += "\n" + it + "\n"
for it in win32_sources:
    win32_source_result += include_headers(headers, lsh_get_file(it))
win32_source_result += "\n#endif\n"

# Add osmesa code
osmesa_source_result = "\n#ifndef _GLFW_OSMESA\n"
osmesa_source_result += "GLFWbool _glfwConnectNull(int platformID, _GLFWplatform* platform) { return GLFW_FALSE; }"
osmesa_source_result += "\n#endif\n"
osmesa_source_result += "\n#ifdef _GLFW_OSMESA\n"
for it in osmesa_sources:
    osmesa_source_result += include_headers(headers, lsh_get_file(it))
osmesa_source_result += "\n#endif\n"

# Add x11 code
x11_source_result = "\n#ifdef _GLFW_X11\n"
for it in x11_sources:
    x11_source_result += include_headers(headers, lsh_get_file(it))
x11_source_result += "\n#endif\n"

# Add wayland code
wayland_source_result = "\n#ifdef _GLFW_WAYLAND\n"
for it in wayland_sources:
    wayland_source_result += include_headers(headers, lsh_get_file(it))
wayland_source_result += "\n#endif\n"

# Add cocoa code
cocoa_source_result = "\n#ifdef _GLFW_COCOA\n"
for it in cocoa_sources:
    cocoa_source_result += include_headers(headers, lsh_get_file(it))
cocoa_source_result += "\n#endif\n"

# Add posix_time code (if linux)
time_source_result = "\n#if !defined _GLFW_COCOA && !defined _GLFW_WIN32\n"
for it in time_sources:
    time_source_result += include_headers(headers, lsh_get_file(it))
time_source_result += "\n#endif\n"

# Add posix_thread code (if linux+osx) (if !win32)
thread_source_result = "\n#if !defined _GLFW_WIN32\n"
for it in thread_sources:
    thread_source_result += include_headers(headers, lsh_get_file(it))
thread_source_result += "\n#endif\n"

# Add posix_module code (if linux+osx) (if !win32)
module_source_result = "\n#if !defined _GLFW_WIN32\n"
for it in module_sources:
    module_source_result += include_headers(headers, lsh_get_file(it))
module_source_result += "\n#endif\n"

# Add posix_poll code (if linux+osx) (if !win32)
poll_source_result = "\n#if !defined _GLFW_WIN32\n"
for it in poll_sources:
    poll_source_result += include_headers(headers, lsh_get_file(it))
poll_source_result += "\n#endif\n"

# Add linux code (if !osx && !win32 && !mesa)
linux_source_result = "\n#if !defined _GLFW_COCOA && !defined _GLFW_WIN32 && !defined _GLFW_OSMESA\n"
for it in linux_sources:
    linux_source_result += include_headers(headers, lsh_get_file(it))
linux_source_result += "\n#endif\n"

# Get the glfw headers
headers_result = open("./glfw/include/GLFW/glfw3.h").read() + "\n" + open("./glfw/include/GLFW/glfw3native.h").read() + "\n"

# Add single header
source_result = "\n#ifdef _GLFW_IMPLEMENTATION\n"

source_result += "\n#if defined(_WIN32) || defined(__CYGWIN__)"
source_result += "\n# define _GLFW_WIN32"
source_result += "\n#endif"

source_result += "\n#if defined(__linux__)"
source_result += "\n#	if !defined(_GLFW_WAYLAND)     // Required for Wayland windowing"
source_result += "\n#       define _GLFW_X11"
source_result += "\n#   endif"
source_result += "\n#endif"

source_result += "\n#if defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__) || defined(__DragonFly__)"
source_result += "\n#	define _GLFW_X11"
source_result += "\n#endif"

source_result += "\n#if defined(__APPLE__)"
source_result += "\n#	define _GLFW_COCOA"
source_result += "\n#	define _GLFW_USE_MENUBAR       // To create and populate the menu bar when the first window is created"
source_result += "\n#	define _GLFW_USE_RETINA        // To have windows use the full resolution of Retina displays"
source_result += "\n#endif"

source_result += "\n#if defined(__TINYC__)"
source_result += "\n#	define _WIN32_WINNT_WINXP      0x0501"
source_result += "\n#endif"

source_result += shared_source_result + win32_source_result + osmesa_source_result + x11_source_result + wayland_source_result + cocoa_source_result
source_result += time_source_result + thread_source_result + module_source_result + poll_source_result + linux_source_result
source_result += "\n#endif\n"

# Comment out options macro error
source_result = source_result.replace("#error \"You must not define any header option macros when compiling GLFW\"",
                                      "//#error \"You must not define any header option macros when compiling GLFW\"")

# for it in win32_headers + osmesa_headers + x11_headers + wayland_headers + cocoa_headers:
#     source_result = source_result.replace(f"#include \"{it}\"", f"//#include \"{it}\"")

source_result = source_result.replace("#include \"../include/GLFW/glfw3.h\"", "//#include \"../include/GLFW/glfw3.h\"")
source_result = source_result.replace("#include \"../include/GLFW/glfw3native.h\"", "")

source_result = source_result.replace("#include \"internal.h\"", "")

# Make dirs
if not os.path.exists("./source"):
    os.makedirs("./source")

# Make single header
open("./glfw.h", "w+").write(headers_result + source_result)

# Make single header + single source
open("./source/glfw.h", "w+").write(headers_result)
open("./source/glfw.c", "w+").write(
    headers_result + "\n#define _GLFW_IMPLEMENTATION\n" + source_result)
