#pragma once

#include <stdexcept>
#include <exception>
#include "fmt/core.h"
#include <string>

#define ThrowRuntimeError(errinfo) throw_runtime_error((errinfo), __LINE__, __FILE__, __FUNCTION__)
#define ThrowInvalidArgument(errinfo) throw_invalid_argument((errinfo), __LINE__, __FILE__, __FUNCTION__)
#define ThrowOutOfRange(errinfo) throw_out_of_range((errinfo), __LINE__, __FILE__, __FUNCTION__)

inline void throw_runtime_error(const std::string &errinfo, int lineno, const char* filename, const char* funcname)
{
    throw std::runtime_error(
        fmt::format(
            "RuntimeError in C++ builtin function {} (File: {} Line: {})\n"
            "Error info: {}", funcname, filename, lineno, errinfo 
    ));
}

inline void throw_invalid_argument(const std::string &errinfo, int lineno, const char* filename, const char* funcname)
{
    throw std::invalid_argument(
        fmt::format(
            "InvalidArgument (ValueError) in C++ builtin function {} (File: {} Line: {})\n"
            "Error info: {}", funcname, filename, lineno, errinfo 
    ));
}

// Not used
inline void throw_length_error(const std::string &errinfo, int lineno, const char* filename, const char* funcname)
{
    throw std::length_error(
        fmt::format(
            "LengthError (ValueError) in C++ builtin function {} (File: {} Line: {})\n"
            "Error info: {}", funcname, filename, lineno, errinfo 
    ));
}

inline void throw_out_of_range(const std::string &errinfo, int lineno, const char* filename, const char* funcname)
{
    throw std::out_of_range(
        fmt::format(
            "OutOfRange (IndexError) in C++ builtin function {} (File: {} Line: {})\n"
            "Error info: {}", funcname, filename, lineno, errinfo 
    ));
}