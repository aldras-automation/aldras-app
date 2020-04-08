// This file contains helper functions that are automatically created from
// templates.

#include "nuitka/prelude.h"

extern PyObject *callPythonFunction( PyObject *func, PyObject **args, int count );


PyObject *CALL_FUNCTION_WITH_ARGS1(PyObject *called, PyObject **args) {
    CHECK_OBJECT(called);

    // Check if arguments are valid objects in debug mode.
#ifndef __NUITKA_NO_ASSERT__
    for (size_t i = 0; i < 1; i++)
    {
        CHECK_OBJECT(args[i]);
    }
#endif

    if (Nuitka_Function_Check(called)) {
        if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
            return NULL;
        }

        struct Nuitka_FunctionObject *function = (struct Nuitka_FunctionObject *)called;
        PyObject *result;

        if (function->m_args_simple && 1 == function->m_args_positional_count){
            for (Py_ssize_t i = 0; i < 1; i++)
            {
                Py_INCREF(args[i]);
            }

            result = function->m_c_code(function, args);
        } else if (function->m_args_simple && 1 + function->m_defaults_given == function->m_args_positional_count) {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
            PyObject *python_pars[function->m_args_positional_count];
#endif
            memcpy(python_pars, args, 1 * sizeof(PyObject *));
            memcpy(python_pars + 1, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

            for (Py_ssize_t i = 0; i < function->m_args_positional_count; i++)
            {
                Py_INCREF(python_pars[i]);
            }

            result = function->m_c_code(function, python_pars);
        } else {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
            PyObject *python_pars[function->m_args_overall_count];
#endif
            memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

            if (parseArgumentsPos(function, python_pars, args, 1)) {
                result = function->m_c_code(function, python_pars);
            } else {
                result = NULL;
            }
        }

        Py_LeaveRecursiveCall();

        return result;
    } else if (Nuitka_Method_Check(called)) {
        struct Nuitka_MethodObject *method = (struct Nuitka_MethodObject *)called;

        // Unbound method without arguments, let the error path be slow.
        if (method->m_object != NULL)
        {
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }

            struct Nuitka_FunctionObject *function = method->m_function;

            PyObject *result;

            if (function->m_args_simple && 1 + 1 == function->m_args_positional_count) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                for (Py_ssize_t i = 0; i < 1; i++) {
                    python_pars[i+1] = args[i];
                    Py_INCREF(args[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else if ( function->m_args_simple && 1 + 1 + function->m_defaults_given == function->m_args_positional_count ) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                memcpy(python_pars+1, args, 1 * sizeof(PyObject *));
                memcpy(python_pars+1 + 1, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

                for (Py_ssize_t i = 1; i < function->m_args_overall_count; i++) {
                    Py_INCREF(python_pars[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
                PyObject *python_pars[function->m_args_overall_count];
#endif
                memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

                if (parseArgumentsMethodPos(function, python_pars, method->m_object, args, 1)) {
                    result = function->m_c_code(function, python_pars);
                } else {
                    result = NULL;
                }
            }

            Py_LeaveRecursiveCall();

            return result;
        }
    } else if (PyCFunction_Check(called)) {
        // Try to be fast about wrapping the arguments.
        int flags = PyCFunction_GET_FLAGS(called) & ~(METH_CLASS | METH_STATIC | METH_COEXIST);

        if (flags & METH_NOARGS) {
#if 1 == 0
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, NULL );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(
                PyExc_TypeError,
                "%s() takes no arguments (1 given)",
                ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_O) {
#if 1 == 1
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, args[0] );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(PyExc_TypeError,
                "%s() takes exactly one argument (1 given)",
                 ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_VARARGS) {
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            PyObject *pos_args = MAKE_TUPLE(args, 1);

            PyObject *result;

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

#if PYTHON_VERSION < 360
            if (flags & METH_KEYWORDS) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else {
                result = (*method)(self, pos_args);
            }
#else
            if (flags == (METH_VARARGS|METH_KEYWORDS)) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else if (flags == METH_FASTCALL) {
#if PYTHON_VERSION < 370
                result = (*(_PyCFunctionFast)method)(self, &PyTuple_GET_ITEM(pos_args, 0), 1, NULL);
#else
                result = (*(_PyCFunctionFast)method)(self, &pos_args, 1);
#endif
            } else {
                result = (*method)(self, pos_args);
            }
#endif

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
                // Some buggy C functions do set an error, but do not indicate it
                // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                Py_DECREF(pos_args);
                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                Py_DECREF(pos_args);
                return NULL;
            }
        }
    } else if (PyFunction_Check(called)) {
        return callPythonFunction(
            called,
            args,
            1
        );
    }

    PyObject *pos_args = MAKE_TUPLE(args, 1);

    PyObject *result = CALL_FUNCTION(called, pos_args, NULL);

    Py_DECREF(pos_args);

    return result;
}

PyObject *CALL_FUNCTION_WITH_ARGS2(PyObject *called, PyObject **args) {
    CHECK_OBJECT(called);

    // Check if arguments are valid objects in debug mode.
#ifndef __NUITKA_NO_ASSERT__
    for (size_t i = 0; i < 2; i++)
    {
        CHECK_OBJECT(args[i]);
    }
#endif

    if (Nuitka_Function_Check(called)) {
        if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
            return NULL;
        }

        struct Nuitka_FunctionObject *function = (struct Nuitka_FunctionObject *)called;
        PyObject *result;

        if (function->m_args_simple && 2 == function->m_args_positional_count){
            for (Py_ssize_t i = 0; i < 2; i++)
            {
                Py_INCREF(args[i]);
            }

            result = function->m_c_code(function, args);
        } else if (function->m_args_simple && 2 + function->m_defaults_given == function->m_args_positional_count) {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
            PyObject *python_pars[function->m_args_positional_count];
#endif
            memcpy(python_pars, args, 2 * sizeof(PyObject *));
            memcpy(python_pars + 2, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

            for (Py_ssize_t i = 0; i < function->m_args_positional_count; i++)
            {
                Py_INCREF(python_pars[i]);
            }

            result = function->m_c_code(function, python_pars);
        } else {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
            PyObject *python_pars[function->m_args_overall_count];
#endif
            memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

            if (parseArgumentsPos(function, python_pars, args, 2)) {
                result = function->m_c_code(function, python_pars);
            } else {
                result = NULL;
            }
        }

        Py_LeaveRecursiveCall();

        return result;
    } else if (Nuitka_Method_Check(called)) {
        struct Nuitka_MethodObject *method = (struct Nuitka_MethodObject *)called;

        // Unbound method without arguments, let the error path be slow.
        if (method->m_object != NULL)
        {
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }

            struct Nuitka_FunctionObject *function = method->m_function;

            PyObject *result;

            if (function->m_args_simple && 2 + 1 == function->m_args_positional_count) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                for (Py_ssize_t i = 0; i < 2; i++) {
                    python_pars[i+1] = args[i];
                    Py_INCREF(args[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else if ( function->m_args_simple && 2 + 1 + function->m_defaults_given == function->m_args_positional_count ) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                memcpy(python_pars+1, args, 2 * sizeof(PyObject *));
                memcpy(python_pars+1 + 2, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

                for (Py_ssize_t i = 1; i < function->m_args_overall_count; i++) {
                    Py_INCREF(python_pars[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
                PyObject *python_pars[function->m_args_overall_count];
#endif
                memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

                if (parseArgumentsMethodPos(function, python_pars, method->m_object, args, 2)) {
                    result = function->m_c_code(function, python_pars);
                } else {
                    result = NULL;
                }
            }

            Py_LeaveRecursiveCall();

            return result;
        }
    } else if (PyCFunction_Check(called)) {
        // Try to be fast about wrapping the arguments.
        int flags = PyCFunction_GET_FLAGS(called) & ~(METH_CLASS | METH_STATIC | METH_COEXIST);

        if (flags & METH_NOARGS) {
#if 2 == 0
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, NULL );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(
                PyExc_TypeError,
                "%s() takes no arguments (2 given)",
                ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_O) {
#if 2 == 1
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, args[0] );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(PyExc_TypeError,
                "%s() takes exactly one argument (2 given)",
                 ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_VARARGS) {
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            PyObject *pos_args = MAKE_TUPLE(args, 2);

            PyObject *result;

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

#if PYTHON_VERSION < 360
            if (flags & METH_KEYWORDS) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else {
                result = (*method)(self, pos_args);
            }
#else
            if (flags == (METH_VARARGS|METH_KEYWORDS)) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else if (flags == METH_FASTCALL) {
#if PYTHON_VERSION < 370
                result = (*(_PyCFunctionFast)method)(self, &PyTuple_GET_ITEM(pos_args, 0), 2, NULL);
#else
                result = (*(_PyCFunctionFast)method)(self, &pos_args, 2);
#endif
            } else {
                result = (*method)(self, pos_args);
            }
#endif

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
                // Some buggy C functions do set an error, but do not indicate it
                // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                Py_DECREF(pos_args);
                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                Py_DECREF(pos_args);
                return NULL;
            }
        }
    } else if (PyFunction_Check(called)) {
        return callPythonFunction(
            called,
            args,
            2
        );
    }

    PyObject *pos_args = MAKE_TUPLE(args, 2);

    PyObject *result = CALL_FUNCTION(called, pos_args, NULL);

    Py_DECREF(pos_args);

    return result;
}

PyObject *CALL_FUNCTION_WITH_ARGS3(PyObject *called, PyObject **args) {
    CHECK_OBJECT(called);

    // Check if arguments are valid objects in debug mode.
#ifndef __NUITKA_NO_ASSERT__
    for (size_t i = 0; i < 3; i++)
    {
        CHECK_OBJECT(args[i]);
    }
#endif

    if (Nuitka_Function_Check(called)) {
        if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
            return NULL;
        }

        struct Nuitka_FunctionObject *function = (struct Nuitka_FunctionObject *)called;
        PyObject *result;

        if (function->m_args_simple && 3 == function->m_args_positional_count){
            for (Py_ssize_t i = 0; i < 3; i++)
            {
                Py_INCREF(args[i]);
            }

            result = function->m_c_code(function, args);
        } else if (function->m_args_simple && 3 + function->m_defaults_given == function->m_args_positional_count) {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
            PyObject *python_pars[function->m_args_positional_count];
#endif
            memcpy(python_pars, args, 3 * sizeof(PyObject *));
            memcpy(python_pars + 3, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

            for (Py_ssize_t i = 0; i < function->m_args_positional_count; i++)
            {
                Py_INCREF(python_pars[i]);
            }

            result = function->m_c_code(function, python_pars);
        } else {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
            PyObject *python_pars[function->m_args_overall_count];
#endif
            memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

            if (parseArgumentsPos(function, python_pars, args, 3)) {
                result = function->m_c_code(function, python_pars);
            } else {
                result = NULL;
            }
        }

        Py_LeaveRecursiveCall();

        return result;
    } else if (Nuitka_Method_Check(called)) {
        struct Nuitka_MethodObject *method = (struct Nuitka_MethodObject *)called;

        // Unbound method without arguments, let the error path be slow.
        if (method->m_object != NULL)
        {
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }

            struct Nuitka_FunctionObject *function = method->m_function;

            PyObject *result;

            if (function->m_args_simple && 3 + 1 == function->m_args_positional_count) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                for (Py_ssize_t i = 0; i < 3; i++) {
                    python_pars[i+1] = args[i];
                    Py_INCREF(args[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else if ( function->m_args_simple && 3 + 1 + function->m_defaults_given == function->m_args_positional_count ) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                memcpy(python_pars+1, args, 3 * sizeof(PyObject *));
                memcpy(python_pars+1 + 3, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

                for (Py_ssize_t i = 1; i < function->m_args_overall_count; i++) {
                    Py_INCREF(python_pars[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
                PyObject *python_pars[function->m_args_overall_count];
#endif
                memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

                if (parseArgumentsMethodPos(function, python_pars, method->m_object, args, 3)) {
                    result = function->m_c_code(function, python_pars);
                } else {
                    result = NULL;
                }
            }

            Py_LeaveRecursiveCall();

            return result;
        }
    } else if (PyCFunction_Check(called)) {
        // Try to be fast about wrapping the arguments.
        int flags = PyCFunction_GET_FLAGS(called) & ~(METH_CLASS | METH_STATIC | METH_COEXIST);

        if (flags & METH_NOARGS) {
#if 3 == 0
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, NULL );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(
                PyExc_TypeError,
                "%s() takes no arguments (3 given)",
                ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_O) {
#if 3 == 1
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, args[0] );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(PyExc_TypeError,
                "%s() takes exactly one argument (3 given)",
                 ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_VARARGS) {
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            PyObject *pos_args = MAKE_TUPLE(args, 3);

            PyObject *result;

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

#if PYTHON_VERSION < 360
            if (flags & METH_KEYWORDS) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else {
                result = (*method)(self, pos_args);
            }
#else
            if (flags == (METH_VARARGS|METH_KEYWORDS)) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else if (flags == METH_FASTCALL) {
#if PYTHON_VERSION < 370
                result = (*(_PyCFunctionFast)method)(self, &PyTuple_GET_ITEM(pos_args, 0), 3, NULL);
#else
                result = (*(_PyCFunctionFast)method)(self, &pos_args, 3);
#endif
            } else {
                result = (*method)(self, pos_args);
            }
#endif

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
                // Some buggy C functions do set an error, but do not indicate it
                // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                Py_DECREF(pos_args);
                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                Py_DECREF(pos_args);
                return NULL;
            }
        }
    } else if (PyFunction_Check(called)) {
        return callPythonFunction(
            called,
            args,
            3
        );
    }

    PyObject *pos_args = MAKE_TUPLE(args, 3);

    PyObject *result = CALL_FUNCTION(called, pos_args, NULL);

    Py_DECREF(pos_args);

    return result;
}

PyObject *CALL_FUNCTION_WITH_ARGS4(PyObject *called, PyObject **args) {
    CHECK_OBJECT(called);

    // Check if arguments are valid objects in debug mode.
#ifndef __NUITKA_NO_ASSERT__
    for (size_t i = 0; i < 4; i++)
    {
        CHECK_OBJECT(args[i]);
    }
#endif

    if (Nuitka_Function_Check(called)) {
        if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
            return NULL;
        }

        struct Nuitka_FunctionObject *function = (struct Nuitka_FunctionObject *)called;
        PyObject *result;

        if (function->m_args_simple && 4 == function->m_args_positional_count){
            for (Py_ssize_t i = 0; i < 4; i++)
            {
                Py_INCREF(args[i]);
            }

            result = function->m_c_code(function, args);
        } else if (function->m_args_simple && 4 + function->m_defaults_given == function->m_args_positional_count) {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
            PyObject *python_pars[function->m_args_positional_count];
#endif
            memcpy(python_pars, args, 4 * sizeof(PyObject *));
            memcpy(python_pars + 4, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

            for (Py_ssize_t i = 0; i < function->m_args_positional_count; i++)
            {
                Py_INCREF(python_pars[i]);
            }

            result = function->m_c_code(function, python_pars);
        } else {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
            PyObject *python_pars[function->m_args_overall_count];
#endif
            memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

            if (parseArgumentsPos(function, python_pars, args, 4)) {
                result = function->m_c_code(function, python_pars);
            } else {
                result = NULL;
            }
        }

        Py_LeaveRecursiveCall();

        return result;
    } else if (Nuitka_Method_Check(called)) {
        struct Nuitka_MethodObject *method = (struct Nuitka_MethodObject *)called;

        // Unbound method without arguments, let the error path be slow.
        if (method->m_object != NULL)
        {
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }

            struct Nuitka_FunctionObject *function = method->m_function;

            PyObject *result;

            if (function->m_args_simple && 4 + 1 == function->m_args_positional_count) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                for (Py_ssize_t i = 0; i < 4; i++) {
                    python_pars[i+1] = args[i];
                    Py_INCREF(args[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else if ( function->m_args_simple && 4 + 1 + function->m_defaults_given == function->m_args_positional_count ) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                memcpy(python_pars+1, args, 4 * sizeof(PyObject *));
                memcpy(python_pars+1 + 4, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

                for (Py_ssize_t i = 1; i < function->m_args_overall_count; i++) {
                    Py_INCREF(python_pars[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
                PyObject *python_pars[function->m_args_overall_count];
#endif
                memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

                if (parseArgumentsMethodPos(function, python_pars, method->m_object, args, 4)) {
                    result = function->m_c_code(function, python_pars);
                } else {
                    result = NULL;
                }
            }

            Py_LeaveRecursiveCall();

            return result;
        }
    } else if (PyCFunction_Check(called)) {
        // Try to be fast about wrapping the arguments.
        int flags = PyCFunction_GET_FLAGS(called) & ~(METH_CLASS | METH_STATIC | METH_COEXIST);

        if (flags & METH_NOARGS) {
#if 4 == 0
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, NULL );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(
                PyExc_TypeError,
                "%s() takes no arguments (4 given)",
                ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_O) {
#if 4 == 1
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, args[0] );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(PyExc_TypeError,
                "%s() takes exactly one argument (4 given)",
                 ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_VARARGS) {
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            PyObject *pos_args = MAKE_TUPLE(args, 4);

            PyObject *result;

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

#if PYTHON_VERSION < 360
            if (flags & METH_KEYWORDS) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else {
                result = (*method)(self, pos_args);
            }
#else
            if (flags == (METH_VARARGS|METH_KEYWORDS)) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else if (flags == METH_FASTCALL) {
#if PYTHON_VERSION < 370
                result = (*(_PyCFunctionFast)method)(self, &PyTuple_GET_ITEM(pos_args, 0), 4, NULL);
#else
                result = (*(_PyCFunctionFast)method)(self, &pos_args, 4);
#endif
            } else {
                result = (*method)(self, pos_args);
            }
#endif

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
                // Some buggy C functions do set an error, but do not indicate it
                // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                Py_DECREF(pos_args);
                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                Py_DECREF(pos_args);
                return NULL;
            }
        }
    } else if (PyFunction_Check(called)) {
        return callPythonFunction(
            called,
            args,
            4
        );
    }

    PyObject *pos_args = MAKE_TUPLE(args, 4);

    PyObject *result = CALL_FUNCTION(called, pos_args, NULL);

    Py_DECREF(pos_args);

    return result;
}

PyObject *CALL_FUNCTION_WITH_ARGS5(PyObject *called, PyObject **args) {
    CHECK_OBJECT(called);

    // Check if arguments are valid objects in debug mode.
#ifndef __NUITKA_NO_ASSERT__
    for (size_t i = 0; i < 5; i++)
    {
        CHECK_OBJECT(args[i]);
    }
#endif

    if (Nuitka_Function_Check(called)) {
        if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
            return NULL;
        }

        struct Nuitka_FunctionObject *function = (struct Nuitka_FunctionObject *)called;
        PyObject *result;

        if (function->m_args_simple && 5 == function->m_args_positional_count){
            for (Py_ssize_t i = 0; i < 5; i++)
            {
                Py_INCREF(args[i]);
            }

            result = function->m_c_code(function, args);
        } else if (function->m_args_simple && 5 + function->m_defaults_given == function->m_args_positional_count) {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
            PyObject *python_pars[function->m_args_positional_count];
#endif
            memcpy(python_pars, args, 5 * sizeof(PyObject *));
            memcpy(python_pars + 5, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

            for (Py_ssize_t i = 0; i < function->m_args_positional_count; i++)
            {
                Py_INCREF(python_pars[i]);
            }

            result = function->m_c_code(function, python_pars);
        } else {
#ifdef _MSC_VER
            PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
            PyObject *python_pars[function->m_args_overall_count];
#endif
            memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

            if (parseArgumentsPos(function, python_pars, args, 5)) {
                result = function->m_c_code(function, python_pars);
            } else {
                result = NULL;
            }
        }

        Py_LeaveRecursiveCall();

        return result;
    } else if (Nuitka_Method_Check(called)) {
        struct Nuitka_MethodObject *method = (struct Nuitka_MethodObject *)called;

        // Unbound method without arguments, let the error path be slow.
        if (method->m_object != NULL)
        {
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }

            struct Nuitka_FunctionObject *function = method->m_function;

            PyObject *result;

            if (function->m_args_simple && 5 + 1 == function->m_args_positional_count) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                for (Py_ssize_t i = 0; i < 5; i++) {
                    python_pars[i+1] = args[i];
                    Py_INCREF(args[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else if ( function->m_args_simple && 5 + 1 + function->m_defaults_given == function->m_args_positional_count ) {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_positional_count);
#else
                PyObject *python_pars[function->m_args_positional_count];
#endif
                python_pars[0] = method->m_object;
                Py_INCREF(method->m_object);

                memcpy(python_pars+1, args, 5 * sizeof(PyObject *));
                memcpy(python_pars+1 + 5, &PyTuple_GET_ITEM(function->m_defaults, 0), function->m_defaults_given * sizeof(PyObject *));

                for (Py_ssize_t i = 1; i < function->m_args_overall_count; i++) {
                    Py_INCREF(python_pars[i]);
                }

                result = function->m_c_code(function, python_pars);
            } else {
#ifdef _MSC_VER
                PyObject **python_pars = (PyObject **)_alloca(sizeof(PyObject *) * function->m_args_overall_count);
#else
                PyObject *python_pars[function->m_args_overall_count];
#endif
                memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

                if (parseArgumentsMethodPos(function, python_pars, method->m_object, args, 5)) {
                    result = function->m_c_code(function, python_pars);
                } else {
                    result = NULL;
                }
            }

            Py_LeaveRecursiveCall();

            return result;
        }
    } else if (PyCFunction_Check(called)) {
        // Try to be fast about wrapping the arguments.
        int flags = PyCFunction_GET_FLAGS(called) & ~(METH_CLASS | METH_STATIC | METH_COEXIST);

        if (flags & METH_NOARGS) {
#if 5 == 0
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, NULL );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(
                PyExc_TypeError,
                "%s() takes no arguments (5 given)",
                ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_O) {
#if 5 == 1
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

            PyObject *result = (*method)( self, args[0] );

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
            // Some buggy C functions do set an error, but do not indicate it
            // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                return NULL;
            }
#else
            PyErr_Format(PyExc_TypeError,
                "%s() takes exactly one argument (5 given)",
                 ((PyCFunctionObject *)called)->m_ml->ml_name
            );
            return NULL;
#endif
        } else if (flags & METH_VARARGS) {
            PyCFunction method = PyCFunction_GET_FUNCTION(called);
            PyObject *self = PyCFunction_GET_SELF(called);

            PyObject *pos_args = MAKE_TUPLE(args, 5);

            PyObject *result;

            // Recursion guard is not strictly necessary, as we already have
            // one on our way to here.
#ifdef _NUITKA_FULL_COMPAT
            if (unlikely(Py_EnterRecursiveCall((char *)" while calling a Python object"))) {
                return NULL;
            }
#endif

#if PYTHON_VERSION < 360
            if (flags & METH_KEYWORDS) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else {
                result = (*method)(self, pos_args);
            }
#else
            if (flags == (METH_VARARGS|METH_KEYWORDS)) {
                result = (*(PyCFunctionWithKeywords)method)(self, pos_args, NULL);
            } else if (flags == METH_FASTCALL) {
#if PYTHON_VERSION < 370
                result = (*(_PyCFunctionFast)method)(self, &PyTuple_GET_ITEM(pos_args, 0), 5, NULL);
#else
                result = (*(_PyCFunctionFast)method)(self, &pos_args, 5);
#endif
            } else {
                result = (*method)(self, pos_args);
            }
#endif

#ifdef _NUITKA_FULL_COMPAT
            Py_LeaveRecursiveCall();
#endif

            if (result != NULL) {
                // Some buggy C functions do set an error, but do not indicate it
                // and Nuitka inner workings can get upset/confused from it.
                DROP_ERROR_OCCURRED();

                Py_DECREF(pos_args);
                return result;
            } else {
                // Other buggy C functions do this, return NULL, but with
                // no error set, not allowed.
                if (unlikely(!ERROR_OCCURRED())) {
                    PyErr_Format(
                        PyExc_SystemError,
                        "NULL result without error in PyObject_Call"
                    );
                }

                Py_DECREF(pos_args);
                return NULL;
            }
        }
    } else if (PyFunction_Check(called)) {
        return callPythonFunction(
            called,
            args,
            5
        );
    }

    PyObject *pos_args = MAKE_TUPLE(args, 5);

    PyObject *result = CALL_FUNCTION(called, pos_args, NULL);

    Py_DECREF(pos_args);

    return result;
}
/* Code to register embedded modules for meta path based loading if any. */

#include "nuitka/unfreezing.h"

/* Table for lookup to find compiled or bytecode modules included in this
 * binary or module, or put along this binary as extension modules. We do
 * our own loading for each of these.
 */
extern PyObject *modulecode___main__(char const *);
static struct Nuitka_MetaPathBasedLoaderEntry meta_path_loader_entries[] =
{
    {"__main__", modulecode___main__, 0, 0, },
    {"_asyncio", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_bz2", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_ctypes", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_decimal", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_elementtree", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_hashlib", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_lzma", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_msi", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_multiprocessing", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_overlapped", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_queue", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_socket", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_sqlite3", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_ssl", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"_tkinter", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"pyexpat", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"select", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"site", NULL, 587, 13161, NUITKA_BYTECODE_FLAG},
    {"unicodedata", NULL, 0, 0, NUITKA_SHLIB_FLAG},
    {"__future__", NULL, 13748, 4143, NUITKA_BYTECODE_FLAG},
    {"_bootlocale", NULL, 17891, 1260, NUITKA_BYTECODE_FLAG},
    {"_compat_pickle", NULL, 19151, 5819, NUITKA_BYTECODE_FLAG},
    {"_dummy_thread", NULL, 24970, 6000, NUITKA_BYTECODE_FLAG},
    {"_markupbase", NULL, 30970, 7796, NUITKA_BYTECODE_FLAG},
    {"_osx_support", NULL, 38766, 9606, NUITKA_BYTECODE_FLAG},
    {"_py_abc", NULL, 48372, 4665, NUITKA_BYTECODE_FLAG},
    {"_pyio", NULL, 53037, 72958, NUITKA_BYTECODE_FLAG},
    {"_sitebuiltins", NULL, 125995, 3476, NUITKA_BYTECODE_FLAG},
    {"_strptime", NULL, 129471, 16115, NUITKA_BYTECODE_FLAG},
    {"_threading_local", NULL, 145586, 6423, NUITKA_BYTECODE_FLAG},
    {"aifc", NULL, 152009, 26154, NUITKA_BYTECODE_FLAG},
    {"argparse", NULL, 178163, 61995, NUITKA_BYTECODE_FLAG},
    {"ast", NULL, 240158, 11747, NUITKA_BYTECODE_FLAG},
    {"asynchat", NULL, 251905, 6845, NUITKA_BYTECODE_FLAG},
    {"asyncio", NULL, 258750, 701, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"asyncio.base_events", NULL, 259451, 48535, NUITKA_BYTECODE_FLAG},
    {"asyncio.base_futures", NULL, 307986, 2113, NUITKA_BYTECODE_FLAG},
    {"asyncio.base_subprocess", NULL, 310099, 9202, NUITKA_BYTECODE_FLAG},
    {"asyncio.base_tasks", NULL, 319301, 1877, NUITKA_BYTECODE_FLAG},
    {"asyncio.constants", NULL, 321178, 602, NUITKA_BYTECODE_FLAG},
    {"asyncio.coroutines", NULL, 321780, 6389, NUITKA_BYTECODE_FLAG},
    {"asyncio.events", NULL, 328169, 27901, NUITKA_BYTECODE_FLAG},
    {"asyncio.format_helpers", NULL, 356070, 2328, NUITKA_BYTECODE_FLAG},
    {"asyncio.futures", NULL, 358398, 10828, NUITKA_BYTECODE_FLAG},
    {"asyncio.locks", NULL, 369226, 15924, NUITKA_BYTECODE_FLAG},
    {"asyncio.log", NULL, 385150, 251, NUITKA_BYTECODE_FLAG},
    {"asyncio.proactor_events", NULL, 385401, 20099, NUITKA_BYTECODE_FLAG},
    {"asyncio.protocols", NULL, 405500, 8739, NUITKA_BYTECODE_FLAG},
    {"asyncio.queues", NULL, 414239, 8184, NUITKA_BYTECODE_FLAG},
    {"asyncio.runners", NULL, 422423, 1953, NUITKA_BYTECODE_FLAG},
    {"asyncio.selector_events", NULL, 424376, 28465, NUITKA_BYTECODE_FLAG},
    {"asyncio.sslproto", NULL, 452841, 21270, NUITKA_BYTECODE_FLAG},
    {"asyncio.streams", NULL, 474111, 20299, NUITKA_BYTECODE_FLAG},
    {"asyncio.subprocess", NULL, 494410, 6763, NUITKA_BYTECODE_FLAG},
    {"asyncio.tasks", NULL, 501173, 22330, NUITKA_BYTECODE_FLAG},
    {"asyncio.transports", NULL, 523503, 12222, NUITKA_BYTECODE_FLAG},
    {"asyncio.windows_events", NULL, 535725, 23079, NUITKA_BYTECODE_FLAG},
    {"asyncio.windows_utils", NULL, 558804, 4412, NUITKA_BYTECODE_FLAG},
    {"asyncore", NULL, 563216, 15855, NUITKA_BYTECODE_FLAG},
    {"bdb", NULL, 579071, 24587, NUITKA_BYTECODE_FLAG},
    {"binhex", NULL, 603658, 12070, NUITKA_BYTECODE_FLAG},
    {"bisect", NULL, 615728, 2709, NUITKA_BYTECODE_FLAG},
    {"cProfile", NULL, 618437, 4819, NUITKA_BYTECODE_FLAG},
    {"calendar", NULL, 623256, 27435, NUITKA_BYTECODE_FLAG},
    {"cgi", NULL, 650691, 27245, NUITKA_BYTECODE_FLAG},
    {"cgitb", NULL, 677936, 10123, NUITKA_BYTECODE_FLAG},
    {"chunk", NULL, 688059, 4930, NUITKA_BYTECODE_FLAG},
    {"cmd", NULL, 692989, 12601, NUITKA_BYTECODE_FLAG},
    {"code", NULL, 705590, 9872, NUITKA_BYTECODE_FLAG},
    {"codeop", NULL, 715462, 6321, NUITKA_BYTECODE_FLAG},
    {"colorsys", NULL, 721783, 3308, NUITKA_BYTECODE_FLAG},
    {"compileall", NULL, 725091, 9345, NUITKA_BYTECODE_FLAG},
    {"concurrent", NULL, 734436, 157, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"concurrent.futures", NULL, 734593, 1097, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"concurrent.futures._base", NULL, 735690, 21195, NUITKA_BYTECODE_FLAG},
    {"concurrent.futures.process", NULL, 756885, 20004, NUITKA_BYTECODE_FLAG},
    {"concurrent.futures.thread", NULL, 776889, 5444, NUITKA_BYTECODE_FLAG},
    {"configparser", NULL, 782333, 45891, NUITKA_BYTECODE_FLAG},
    {"contextlib", NULL, 828224, 20469, NUITKA_BYTECODE_FLAG},
    {"contextvars", NULL, 848693, 268, NUITKA_BYTECODE_FLAG},
    {"copy", NULL, 848961, 7134, NUITKA_BYTECODE_FLAG},
    {"csv", NULL, 856095, 11843, NUITKA_BYTECODE_FLAG},
    {"ctypes", NULL, 867938, 16390, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"ctypes._aix", NULL, 884328, 9834, NUITKA_BYTECODE_FLAG},
    {"ctypes._endian", NULL, 894162, 1967, NUITKA_BYTECODE_FLAG},
    {"ctypes.macholib", NULL, 896129, 324, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"ctypes.macholib.dyld", NULL, 896453, 4371, NUITKA_BYTECODE_FLAG},
    {"ctypes.macholib.dylib", NULL, 900824, 1951, NUITKA_BYTECODE_FLAG},
    {"ctypes.macholib.framework", NULL, 902775, 2231, NUITKA_BYTECODE_FLAG},
    {"ctypes.util", NULL, 905006, 7760, NUITKA_BYTECODE_FLAG},
    {"ctypes.wintypes", NULL, 912766, 5128, NUITKA_BYTECODE_FLAG},
    {"dataclasses", NULL, 917894, 23035, NUITKA_BYTECODE_FLAG},
    {"datetime", NULL, 940929, 57238, NUITKA_BYTECODE_FLAG},
    {"dbm", NULL, 998167, 4177, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"dbm.dumb", NULL, 1002344, 8411, NUITKA_BYTECODE_FLAG},
    {"decimal", NULL, 1010755, 162215, NUITKA_BYTECODE_FLAG},
    {"difflib", NULL, 1172970, 59455, NUITKA_BYTECODE_FLAG},
    {"distutils", NULL, 1232425, 409, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"distutils._msvccompiler", NULL, 1232834, 12651, NUITKA_BYTECODE_FLAG},
    {"distutils.archive_util", NULL, 1245485, 6543, NUITKA_BYTECODE_FLAG},
    {"distutils.bcppcompiler", NULL, 1252028, 6512, NUITKA_BYTECODE_FLAG},
    {"distutils.ccompiler", NULL, 1258540, 33245, NUITKA_BYTECODE_FLAG},
    {"distutils.cmd", NULL, 1291785, 13919, NUITKA_BYTECODE_FLAG},
    {"distutils.command", NULL, 1305704, 566, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"distutils.command.bdist", NULL, 1306270, 3665, NUITKA_BYTECODE_FLAG},
    {"distutils.command.bdist_dumb", NULL, 1309935, 3580, NUITKA_BYTECODE_FLAG},
    {"distutils.command.bdist_msi", NULL, 1313515, 19412, NUITKA_BYTECODE_FLAG},
    {"distutils.command.bdist_rpm", NULL, 1332927, 12505, NUITKA_BYTECODE_FLAG},
    {"distutils.command.bdist_wininst", NULL, 1345432, 8061, NUITKA_BYTECODE_FLAG},
    {"distutils.command.build", NULL, 1353493, 3854, NUITKA_BYTECODE_FLAG},
    {"distutils.command.build_clib", NULL, 1357347, 4896, NUITKA_BYTECODE_FLAG},
    {"distutils.command.build_ext", NULL, 1362243, 15803, NUITKA_BYTECODE_FLAG},
    {"distutils.command.build_py", NULL, 1378046, 10402, NUITKA_BYTECODE_FLAG},
    {"distutils.command.build_scripts", NULL, 1388448, 4301, NUITKA_BYTECODE_FLAG},
    {"distutils.command.check", NULL, 1392749, 4850, NUITKA_BYTECODE_FLAG},
    {"distutils.command.clean", NULL, 1397599, 2103, NUITKA_BYTECODE_FLAG},
    {"distutils.command.config", NULL, 1399702, 10207, NUITKA_BYTECODE_FLAG},
    {"distutils.command.install", NULL, 1409909, 13530, NUITKA_BYTECODE_FLAG},
    {"distutils.command.install_data", NULL, 1423439, 2296, NUITKA_BYTECODE_FLAG},
    {"distutils.command.install_egg_info", NULL, 1425735, 2994, NUITKA_BYTECODE_FLAG},
    {"distutils.command.install_headers", NULL, 1428729, 1711, NUITKA_BYTECODE_FLAG},
    {"distutils.command.install_lib", NULL, 1430440, 5089, NUITKA_BYTECODE_FLAG},
    {"distutils.command.install_scripts", NULL, 1435529, 2153, NUITKA_BYTECODE_FLAG},
    {"distutils.command.register", NULL, 1437682, 8488, NUITKA_BYTECODE_FLAG},
    {"distutils.command.sdist", NULL, 1446170, 14519, NUITKA_BYTECODE_FLAG},
    {"distutils.command.upload", NULL, 1460689, 5101, NUITKA_BYTECODE_FLAG},
    {"distutils.config", NULL, 1465790, 3496, NUITKA_BYTECODE_FLAG},
    {"distutils.core", NULL, 1469286, 6621, NUITKA_BYTECODE_FLAG},
    {"distutils.cygwinccompiler", NULL, 1475907, 8539, NUITKA_BYTECODE_FLAG},
    {"distutils.debug", NULL, 1484446, 219, NUITKA_BYTECODE_FLAG},
    {"distutils.dep_util", NULL, 1484665, 2735, NUITKA_BYTECODE_FLAG},
    {"distutils.dir_util", NULL, 1487400, 5829, NUITKA_BYTECODE_FLAG},
    {"distutils.dist", NULL, 1493229, 34450, NUITKA_BYTECODE_FLAG},
    {"distutils.errors", NULL, 1527679, 5505, NUITKA_BYTECODE_FLAG},
    {"distutils.extension", NULL, 1533184, 6916, NUITKA_BYTECODE_FLAG},
    {"distutils.fancy_getopt", NULL, 1540100, 10628, NUITKA_BYTECODE_FLAG},
    {"distutils.file_util", NULL, 1550728, 5914, NUITKA_BYTECODE_FLAG},
    {"distutils.filelist", NULL, 1556642, 9849, NUITKA_BYTECODE_FLAG},
    {"distutils.log", NULL, 1566491, 2330, NUITKA_BYTECODE_FLAG},
    {"distutils.msvc9compiler", NULL, 1568821, 17394, NUITKA_BYTECODE_FLAG},
    {"distutils.msvccompiler", NULL, 1586215, 14582, NUITKA_BYTECODE_FLAG},
    {"distutils.spawn", NULL, 1600797, 5133, NUITKA_BYTECODE_FLAG},
    {"distutils.sysconfig", NULL, 1605930, 12007, NUITKA_BYTECODE_FLAG},
    {"distutils.text_file", NULL, 1617937, 8456, NUITKA_BYTECODE_FLAG},
    {"distutils.unixccompiler", NULL, 1626393, 6551, NUITKA_BYTECODE_FLAG},
    {"distutils.util", NULL, 1632944, 15112, NUITKA_BYTECODE_FLAG},
    {"distutils.version", NULL, 1648056, 7367, NUITKA_BYTECODE_FLAG},
    {"distutils.versionpredicate", NULL, 1655423, 5114, NUITKA_BYTECODE_FLAG},
    {"doctest", NULL, 1660537, 75449, NUITKA_BYTECODE_FLAG},
    {"dummy_threading", NULL, 1735986, 1135, NUITKA_BYTECODE_FLAG},
    {"email", NULL, 1737121, 1702, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"email._encoded_words", NULL, 1738823, 5619, NUITKA_BYTECODE_FLAG},
    {"email._header_value_parser", NULL, 1744442, 76835, NUITKA_BYTECODE_FLAG},
    {"email._parseaddr", NULL, 1821277, 12416, NUITKA_BYTECODE_FLAG},
    {"email._policybase", NULL, 1833693, 14861, NUITKA_BYTECODE_FLAG},
    {"email.base64mime", NULL, 1848554, 3246, NUITKA_BYTECODE_FLAG},
    {"email.charset", NULL, 1851800, 11540, NUITKA_BYTECODE_FLAG},
    {"email.contentmanager", NULL, 1863340, 7306, NUITKA_BYTECODE_FLAG},
    {"email.encoders", NULL, 1870646, 1675, NUITKA_BYTECODE_FLAG},
    {"email.errors", NULL, 1872321, 6202, NUITKA_BYTECODE_FLAG},
    {"email.feedparser", NULL, 1878523, 10640, NUITKA_BYTECODE_FLAG},
    {"email.generator", NULL, 1889163, 12511, NUITKA_BYTECODE_FLAG},
    {"email.header", NULL, 1901674, 16397, NUITKA_BYTECODE_FLAG},
    {"email.headerregistry", NULL, 1918071, 21308, NUITKA_BYTECODE_FLAG},
    {"email.iterators", NULL, 1939379, 1943, NUITKA_BYTECODE_FLAG},
    {"email.message", NULL, 1941322, 38005, NUITKA_BYTECODE_FLAG},
    {"email.mime", NULL, 1979327, 157, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"email.mime.application", NULL, 1979484, 1468, NUITKA_BYTECODE_FLAG},
    {"email.mime.audio", NULL, 1980952, 2627, NUITKA_BYTECODE_FLAG},
    {"email.mime.base", NULL, 1983579, 1093, NUITKA_BYTECODE_FLAG},
    {"email.mime.image", NULL, 1984672, 1913, NUITKA_BYTECODE_FLAG},
    {"email.mime.message", NULL, 1986585, 1342, NUITKA_BYTECODE_FLAG},
    {"email.mime.multipart", NULL, 1987927, 1564, NUITKA_BYTECODE_FLAG},
    {"email.mime.nonmultipart", NULL, 1989491, 779, NUITKA_BYTECODE_FLAG},
    {"email.mime.text", NULL, 1990270, 1326, NUITKA_BYTECODE_FLAG},
    {"email.parser", NULL, 1991596, 5758, NUITKA_BYTECODE_FLAG},
    {"email.policy", NULL, 1997354, 9666, NUITKA_BYTECODE_FLAG},
    {"email.quoprimime", NULL, 2007020, 7675, NUITKA_BYTECODE_FLAG},
    {"email.utils", NULL, 2014695, 9478, NUITKA_BYTECODE_FLAG},
    {"filecmp", NULL, 2024173, 8318, NUITKA_BYTECODE_FLAG},
    {"fileinput", NULL, 2032491, 13266, NUITKA_BYTECODE_FLAG},
    {"fnmatch", NULL, 2045757, 3348, NUITKA_BYTECODE_FLAG},
    {"formatter", NULL, 2049105, 17564, NUITKA_BYTECODE_FLAG},
    {"fractions", NULL, 2066669, 18440, NUITKA_BYTECODE_FLAG},
    {"ftplib", NULL, 2085109, 28078, NUITKA_BYTECODE_FLAG},
    {"getopt", NULL, 2113187, 6250, NUITKA_BYTECODE_FLAG},
    {"getpass", NULL, 2119437, 4175, NUITKA_BYTECODE_FLAG},
    {"gettext", NULL, 2123612, 14179, NUITKA_BYTECODE_FLAG},
    {"glob", NULL, 2137791, 4270, NUITKA_BYTECODE_FLAG},
    {"gzip", NULL, 2142061, 17366, NUITKA_BYTECODE_FLAG},
    {"hashlib", NULL, 2159427, 6602, NUITKA_BYTECODE_FLAG},
    {"hmac", NULL, 2166029, 6124, NUITKA_BYTECODE_FLAG},
    {"html", NULL, 2172153, 3408, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"html.entities", NULL, 2175561, 50480, NUITKA_BYTECODE_FLAG},
    {"html.parser", NULL, 2226041, 11118, NUITKA_BYTECODE_FLAG},
    {"http", NULL, 2237159, 5933, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"http.client", NULL, 2243092, 34661, NUITKA_BYTECODE_FLAG},
    {"http.cookiejar", NULL, 2277753, 53644, NUITKA_BYTECODE_FLAG},
    {"http.cookies", NULL, 2331397, 15255, NUITKA_BYTECODE_FLAG},
    {"http.server", NULL, 2346652, 33378, NUITKA_BYTECODE_FLAG},
    {"imaplib", NULL, 2380030, 41441, NUITKA_BYTECODE_FLAG},
    {"imghdr", NULL, 2421471, 4153, NUITKA_BYTECODE_FLAG},
    {"imp", NULL, 2425624, 9764, NUITKA_BYTECODE_FLAG},
    {"importlib.abc", NULL, 2435388, 13498, NUITKA_BYTECODE_FLAG},
    {"importlib.resources", NULL, 2448886, 8350, NUITKA_BYTECODE_FLAG},
    {"importlib.util", NULL, 2457236, 9367, NUITKA_BYTECODE_FLAG},
    {"ipaddress", NULL, 2466603, 62814, NUITKA_BYTECODE_FLAG},
    {"json", NULL, 2529417, 12349, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"json.decoder", NULL, 2541766, 9835, NUITKA_BYTECODE_FLAG},
    {"json.encoder", NULL, 2551601, 11317, NUITKA_BYTECODE_FLAG},
    {"json.scanner", NULL, 2562918, 2007, NUITKA_BYTECODE_FLAG},
    {"json.tool", NULL, 2564925, 1515, NUITKA_BYTECODE_FLAG},
    {"lib2to3", NULL, 2566440, 154, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"lib2to3.btm_matcher", NULL, 2566594, 4904, NUITKA_BYTECODE_FLAG},
    {"lib2to3.btm_utils", NULL, 2571498, 6154, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixer_base", NULL, 2577652, 6246, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixer_util", NULL, 2583898, 12057, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes", NULL, 2595955, 160, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"lib2to3.fixes.fix_apply", NULL, 2596115, 1679, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_asserts", NULL, 2597794, 1283, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_basestring", NULL, 2599077, 673, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_buffer", NULL, 2599750, 818, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_dict", NULL, 2600568, 3326, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_except", NULL, 2603894, 2828, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_exec", NULL, 2606722, 1159, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_execfile", NULL, 2607881, 1703, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_exitfunc", NULL, 2609584, 2306, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_filter", NULL, 2611890, 2452, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_funcattrs", NULL, 2614342, 984, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_future", NULL, 2615326, 794, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_getcwdu", NULL, 2616120, 798, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_has_key", NULL, 2616918, 2928, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_idioms", NULL, 2619846, 3913, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_import", NULL, 2623759, 2795, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_imports", NULL, 2626554, 4359, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_imports2", NULL, 2630913, 558, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_input", NULL, 2631471, 960, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_intern", NULL, 2632431, 1142, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_isinstance", NULL, 2633573, 1565, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_itertools", NULL, 2635138, 1554, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_itertools_imports", NULL, 2636692, 1590, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_long", NULL, 2638282, 715, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_map", NULL, 2638997, 3103, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_metaclass", NULL, 2642100, 5356, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_methodattrs", NULL, 2647456, 946, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_ne", NULL, 2648402, 817, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_next", NULL, 2649219, 3070, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_nonzero", NULL, 2652289, 933, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_numliterals", NULL, 2653222, 1029, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_operator", NULL, 2654251, 4246, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_paren", NULL, 2658497, 1400, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_print", NULL, 2659897, 2335, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_raise", NULL, 2662232, 2259, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_raw_input", NULL, 2664491, 805, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_reduce", NULL, 2665296, 1140, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_reload", NULL, 2666436, 1154, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_renames", NULL, 2667590, 2003, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_repr", NULL, 2669593, 855, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_set_literal", NULL, 2670448, 1687, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_standarderror", NULL, 2672135, 730, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_sys_exc", NULL, 2672865, 1411, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_throw", NULL, 2674276, 1812, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_tuple_params", NULL, 2676088, 4606, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_types", NULL, 2680694, 1839, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_unicode", NULL, 2682533, 1551, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_urllib", NULL, 2684084, 5971, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_ws_comma", NULL, 2690055, 1133, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_xrange", NULL, 2691188, 2546, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_xreadlines", NULL, 2693734, 1127, NUITKA_BYTECODE_FLAG},
    {"lib2to3.fixes.fix_zip", NULL, 2694861, 1591, NUITKA_BYTECODE_FLAG},
    {"lib2to3.main", NULL, 2696452, 8547, NUITKA_BYTECODE_FLAG},
    {"lib2to3.patcomp", NULL, 2704999, 5622, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2", NULL, 2710621, 190, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"lib2to3.pgen2.driver", NULL, 2710811, 5151, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2.grammar", NULL, 2715962, 7027, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2.literals", NULL, 2722989, 1569, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2.parse", NULL, 2724558, 6315, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2.pgen", NULL, 2730873, 9791, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2.token", NULL, 2740664, 1883, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pgen2.tokenize", NULL, 2742547, 15150, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pygram", NULL, 2757697, 1209, NUITKA_BYTECODE_FLAG},
    {"lib2to3.pytree", NULL, 2758906, 25014, NUITKA_BYTECODE_FLAG},
    {"lib2to3.refactor", NULL, 2783920, 20376, NUITKA_BYTECODE_FLAG},
    {"logging", NULL, 2804296, 62423, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"logging.config", NULL, 2866719, 23086, NUITKA_BYTECODE_FLAG},
    {"logging.handlers", NULL, 2889805, 43043, NUITKA_BYTECODE_FLAG},
    {"lzma", NULL, 2932848, 11950, NUITKA_BYTECODE_FLAG},
    {"macpath", NULL, 2944798, 5818, NUITKA_BYTECODE_FLAG},
    {"mailbox", NULL, 2950616, 63659, NUITKA_BYTECODE_FLAG},
    {"mailcap", NULL, 3014275, 6495, NUITKA_BYTECODE_FLAG},
    {"mimetypes", NULL, 3020770, 15738, NUITKA_BYTECODE_FLAG},
    {"modulefinder", NULL, 3036508, 15363, NUITKA_BYTECODE_FLAG},
    {"msilib", NULL, 3051871, 15848, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"msilib.schema", NULL, 3067719, 56980, NUITKA_BYTECODE_FLAG},
    {"msilib.sequence", NULL, 3124699, 2635, NUITKA_BYTECODE_FLAG},
    {"msilib.text", NULL, 3127334, 8992, NUITKA_BYTECODE_FLAG},
    {"multiprocessing", NULL, 3136326, 538, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"multiprocessing.connection", NULL, 3136864, 24943, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.context", NULL, 3161807, 13124, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.dummy", NULL, 3174931, 3816, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"multiprocessing.dummy.connection", NULL, 3178747, 2524, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.forkserver", NULL, 3181271, 7775, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.heap", NULL, 3189046, 6435, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.managers", NULL, 3195481, 34376, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.pool", NULL, 3229857, 21247, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.popen_spawn_win32", NULL, 3251104, 3443, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.process", NULL, 3254547, 9437, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.queues", NULL, 3263984, 9448, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.reduction", NULL, 3273432, 8029, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.resource_sharer", NULL, 3281461, 5215, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.semaphore_tracker", NULL, 3286676, 3751, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.sharedctypes", NULL, 3290427, 6928, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.spawn", NULL, 3297355, 6479, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.synchronize", NULL, 3303834, 11194, NUITKA_BYTECODE_FLAG},
    {"multiprocessing.util", NULL, 3315028, 10143, NUITKA_BYTECODE_FLAG},
    {"netrc", NULL, 3325171, 3774, NUITKA_BYTECODE_FLAG},
    {"nntplib", NULL, 3328945, 33761, NUITKA_BYTECODE_FLAG},
    {"nturl2path", NULL, 3362706, 1626, NUITKA_BYTECODE_FLAG},
    {"numbers", NULL, 3364332, 12203, NUITKA_BYTECODE_FLAG},
    {"optparse", NULL, 3376535, 47904, NUITKA_BYTECODE_FLAG},
    {"pathlib", NULL, 3424439, 42225, NUITKA_BYTECODE_FLAG},
    {"pdb", NULL, 3466664, 46901, NUITKA_BYTECODE_FLAG},
    {"pickle", NULL, 3513565, 43052, NUITKA_BYTECODE_FLAG},
    {"pickletools", NULL, 3556617, 65342, NUITKA_BYTECODE_FLAG},
    {"pipes", NULL, 3621959, 7814, NUITKA_BYTECODE_FLAG},
    {"pkgutil", NULL, 3629773, 16371, NUITKA_BYTECODE_FLAG},
    {"platform", NULL, 3646144, 28175, NUITKA_BYTECODE_FLAG},
    {"plistlib", NULL, 3674319, 25123, NUITKA_BYTECODE_FLAG},
    {"poplib", NULL, 3699442, 13347, NUITKA_BYTECODE_FLAG},
    {"posixpath", NULL, 3712789, 10440, NUITKA_BYTECODE_FLAG},
    {"pprint", NULL, 3723229, 15844, NUITKA_BYTECODE_FLAG},
    {"profile", NULL, 3739073, 14103, NUITKA_BYTECODE_FLAG},
    {"pstats", NULL, 3753176, 22305, NUITKA_BYTECODE_FLAG},
    {"py_compile", NULL, 3775481, 7202, NUITKA_BYTECODE_FLAG},
    {"pyclbr", NULL, 3782683, 10384, NUITKA_BYTECODE_FLAG},
    {"pydoc", NULL, 3793067, 84415, NUITKA_BYTECODE_FLAG},
    {"pydoc_data", NULL, 3877482, 157, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"pydoc_data.topics", NULL, 3877639, 414270, NUITKA_BYTECODE_FLAG},
    {"queue", NULL, 4291909, 11483, NUITKA_BYTECODE_FLAG},
    {"random", NULL, 4303392, 19419, NUITKA_BYTECODE_FLAG},
    {"rlcompleter", NULL, 4322811, 5758, NUITKA_BYTECODE_FLAG},
    {"runpy", NULL, 4328569, 7956, NUITKA_BYTECODE_FLAG},
    {"sched", NULL, 4336525, 6532, NUITKA_BYTECODE_FLAG},
    {"secrets", NULL, 4343057, 2195, NUITKA_BYTECODE_FLAG},
    {"selectors", NULL, 4345252, 16959, NUITKA_BYTECODE_FLAG},
    {"shelve", NULL, 4362211, 9517, NUITKA_BYTECODE_FLAG},
    {"shlex", NULL, 4371728, 7196, NUITKA_BYTECODE_FLAG},
    {"shutil", NULL, 4378924, 30991, NUITKA_BYTECODE_FLAG},
    {"signal", NULL, 4409915, 2523, NUITKA_BYTECODE_FLAG},
    {"site", NULL, 587, 13161, NUITKA_BYTECODE_FLAG},
    {"smtpd", NULL, 4412438, 26615, NUITKA_BYTECODE_FLAG},
    {"smtplib", NULL, 4439053, 35363, NUITKA_BYTECODE_FLAG},
    {"sndhdr", NULL, 4474416, 6914, NUITKA_BYTECODE_FLAG},
    {"socket", NULL, 4481330, 22048, NUITKA_BYTECODE_FLAG},
    {"socketserver", NULL, 4503378, 24211, NUITKA_BYTECODE_FLAG},
    {"sqlite3", NULL, 4527589, 185, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"sqlite3.dbapi2", NULL, 4527774, 2504, NUITKA_BYTECODE_FLAG},
    {"sqlite3.dump", NULL, 4530278, 1947, NUITKA_BYTECODE_FLAG},
    {"ssl", NULL, 4532225, 39401, NUITKA_BYTECODE_FLAG},
    {"statistics", NULL, 4571626, 18175, NUITKA_BYTECODE_FLAG},
    {"string", NULL, 4589801, 7846, NUITKA_BYTECODE_FLAG},
    {"subprocess", NULL, 4597647, 39225, NUITKA_BYTECODE_FLAG},
    {"sunau", NULL, 4636872, 17222, NUITKA_BYTECODE_FLAG},
    {"symbol", NULL, 4654094, 2576, NUITKA_BYTECODE_FLAG},
    {"symtable", NULL, 4656670, 10456, NUITKA_BYTECODE_FLAG},
    {"sysconfig", NULL, 4667126, 15455, NUITKA_BYTECODE_FLAG},
    {"tabnanny", NULL, 4682581, 6989, NUITKA_BYTECODE_FLAG},
    {"tarfile", NULL, 4689570, 61870, NUITKA_BYTECODE_FLAG},
    {"telnetlib", NULL, 4751440, 18113, NUITKA_BYTECODE_FLAG},
    {"tempfile", NULL, 4769553, 22243, NUITKA_BYTECODE_FLAG},
    {"textwrap", NULL, 4791796, 13536, NUITKA_BYTECODE_FLAG},
    {"this", NULL, 4805332, 1288, NUITKA_BYTECODE_FLAG},
    {"timeit", NULL, 4806620, 11658, NUITKA_BYTECODE_FLAG},
    {"tkinter", NULL, 4818278, 179189, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"tkinter.colorchooser", NULL, 4997467, 1146, NUITKA_BYTECODE_FLAG},
    {"tkinter.commondialog", NULL, 4998613, 1127, NUITKA_BYTECODE_FLAG},
    {"tkinter.constants", NULL, 4999740, 1679, NUITKA_BYTECODE_FLAG},
    {"tkinter.dialog", NULL, 5001419, 1455, NUITKA_BYTECODE_FLAG},
    {"tkinter.dnd", NULL, 5002874, 11197, NUITKA_BYTECODE_FLAG},
    {"tkinter.filedialog", NULL, 5014071, 12281, NUITKA_BYTECODE_FLAG},
    {"tkinter.font", NULL, 5026352, 6198, NUITKA_BYTECODE_FLAG},
    {"tkinter.messagebox", NULL, 5032550, 3063, NUITKA_BYTECODE_FLAG},
    {"tkinter.scrolledtext", NULL, 5035613, 2190, NUITKA_BYTECODE_FLAG},
    {"tkinter.simpledialog", NULL, 5037803, 10557, NUITKA_BYTECODE_FLAG},
    {"tkinter.tix", NULL, 5048360, 83679, NUITKA_BYTECODE_FLAG},
    {"tkinter.ttk", NULL, 5132039, 57903, NUITKA_BYTECODE_FLAG},
    {"trace", NULL, 5189942, 19331, NUITKA_BYTECODE_FLAG},
    {"tracemalloc", NULL, 5209273, 17287, NUITKA_BYTECODE_FLAG},
    {"turtle", NULL, 5226560, 130802, NUITKA_BYTECODE_FLAG},
    {"typing", NULL, 5357362, 50981, NUITKA_BYTECODE_FLAG},
    {"unittest", NULL, 5408343, 3022, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"unittest.case", NULL, 5411365, 48373, NUITKA_BYTECODE_FLAG},
    {"unittest.loader", NULL, 5459738, 14287, NUITKA_BYTECODE_FLAG},
    {"unittest.main", NULL, 5474025, 7449, NUITKA_BYTECODE_FLAG},
    {"unittest.mock", NULL, 5481474, 64976, NUITKA_BYTECODE_FLAG},
    {"unittest.result", NULL, 5546450, 7263, NUITKA_BYTECODE_FLAG},
    {"unittest.runner", NULL, 5553713, 7006, NUITKA_BYTECODE_FLAG},
    {"unittest.signals", NULL, 5560719, 2205, NUITKA_BYTECODE_FLAG},
    {"unittest.suite", NULL, 5562924, 9214, NUITKA_BYTECODE_FLAG},
    {"unittest.util", NULL, 5572138, 4532, NUITKA_BYTECODE_FLAG},
    {"urllib", NULL, 5576670, 153, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"urllib.error", NULL, 5576823, 2787, NUITKA_BYTECODE_FLAG},
    {"urllib.parse", NULL, 5579610, 30849, NUITKA_BYTECODE_FLAG},
    {"urllib.request", NULL, 5610459, 72163, NUITKA_BYTECODE_FLAG},
    {"urllib.response", NULL, 5682622, 3260, NUITKA_BYTECODE_FLAG},
    {"urllib.robotparser", NULL, 5685882, 7100, NUITKA_BYTECODE_FLAG},
    {"uu", NULL, 5692982, 3636, NUITKA_BYTECODE_FLAG},
    {"uuid", NULL, 5696618, 23214, NUITKA_BYTECODE_FLAG},
    {"venv", NULL, 5719832, 14466, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"wave", NULL, 5734298, 18300, NUITKA_BYTECODE_FLAG},
    {"weakref", NULL, 5752598, 19580, NUITKA_BYTECODE_FLAG},
    {"webbrowser", NULL, 5772178, 16386, NUITKA_BYTECODE_FLAG},
    {"wsgiref", NULL, 5788564, 749, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"wsgiref.handlers", NULL, 5789313, 16301, NUITKA_BYTECODE_FLAG},
    {"wsgiref.headers", NULL, 5805614, 7770, NUITKA_BYTECODE_FLAG},
    {"wsgiref.simple_server", NULL, 5813384, 5216, NUITKA_BYTECODE_FLAG},
    {"wsgiref.util", NULL, 5818600, 5191, NUITKA_BYTECODE_FLAG},
    {"wsgiref.validate", NULL, 5823791, 14687, NUITKA_BYTECODE_FLAG},
    {"xdrlib", NULL, 5838478, 8335, NUITKA_BYTECODE_FLAG},
    {"xml", NULL, 5846813, 717, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"xml.dom", NULL, 5847530, 5469, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"xml.dom.NodeFilter", NULL, 5852999, 984, NUITKA_BYTECODE_FLAG},
    {"xml.dom.domreg", NULL, 5853983, 2861, NUITKA_BYTECODE_FLAG},
    {"xml.dom.expatbuilder", NULL, 5856844, 27031, NUITKA_BYTECODE_FLAG},
    {"xml.dom.minicompat", NULL, 5883875, 2830, NUITKA_BYTECODE_FLAG},
    {"xml.dom.minidom", NULL, 5886705, 55630, NUITKA_BYTECODE_FLAG},
    {"xml.dom.pulldom", NULL, 5942335, 10503, NUITKA_BYTECODE_FLAG},
    {"xml.dom.xmlbuilder", NULL, 5952838, 12450, NUITKA_BYTECODE_FLAG},
    {"xml.etree", NULL, 5965288, 156, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"xml.etree.ElementInclude", NULL, 5965444, 1592, NUITKA_BYTECODE_FLAG},
    {"xml.etree.ElementPath", NULL, 5967036, 6360, NUITKA_BYTECODE_FLAG},
    {"xml.etree.ElementTree", NULL, 5973396, 44824, NUITKA_BYTECODE_FLAG},
    {"xml.etree.cElementTree", NULL, 6018220, 198, NUITKA_BYTECODE_FLAG},
    {"xml.parsers", NULL, 6018418, 330, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"xml.parsers.expat", NULL, 6018748, 359, NUITKA_BYTECODE_FLAG},
    {"xml.sax", NULL, 6019107, 3189, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"xml.sax._exceptions", NULL, 6022296, 5498, NUITKA_BYTECODE_FLAG},
    {"xml.sax.expatreader", NULL, 6027794, 12401, NUITKA_BYTECODE_FLAG},
    {"xml.sax.handler", NULL, 6040195, 12374, NUITKA_BYTECODE_FLAG},
    {"xml.sax.saxutils", NULL, 6052569, 12827, NUITKA_BYTECODE_FLAG},
    {"xml.sax.xmlreader", NULL, 6065396, 16935, NUITKA_BYTECODE_FLAG},
    {"xmlrpc", NULL, 6082331, 153, NUITKA_BYTECODE_FLAG | NUITKA_PACKAGE_FLAG},
    {"xmlrpc.client", NULL, 6082484, 34559, NUITKA_BYTECODE_FLAG},
    {"xmlrpc.server", NULL, 6117043, 29433, NUITKA_BYTECODE_FLAG},
    {"zipapp", NULL, 6146476, 5814, NUITKA_BYTECODE_FLAG},
    {"zipfile", NULL, 6152290, 50343, NUITKA_BYTECODE_FLAG},
    {NULL, NULL, 0, 0, 0}
};

void setupMetaPathBasedLoader(void) {
    static bool init_done = false;

    if (init_done == false)
    {
        registerMetaPathBasedUnfreezer(meta_path_loader_entries);
        init_done = true;
    }
}
