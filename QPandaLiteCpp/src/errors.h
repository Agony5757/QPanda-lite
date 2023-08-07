#pragma once

#include <stdexcept>
#include <exception>
#include "fmt/core.h"
#include <string>

#define ThrowRuntimeError(errinfo) throw_runtime_error((errinfo), __LINE__, __FILE__, __FUNCTION__)

inline void throw_runtime_error(const std::string &errinfo, int lineno, const char* filename, const char* funcname)
{
    throw std::runtime_error(
        fmt::format(
            "RuntimeError in C++ builtin function {} (File: {} Line: {})\n"
            "Error info: {}", funcname, filename, lineno, errinfo 
    ));
}