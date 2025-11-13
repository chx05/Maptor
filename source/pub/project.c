#ifndef MPT_PROJECT_C
#define MPT_PROJECT_C

    #include "base.c"

    // TODO:
    // types_t deve essere un array di type_t, ma soa
    // type_t deve essere una lista di istruzioni asl (abstract syntax list)

    typedef struct
    {
        seq_t(str_t) names;
        seq_t(types_t) return_types;
        
        uint32_t cap;
        uint32_t count;
    } functions_t;

    typedef struct
    {
        seq_t(str_t) names;
        seq_t(field_names_t) field_names;
        seq_t(types_t) field_types;
        
        uint32_t cap;
        uint32_t count;
    } structs_t;

    typedef struct
    {
        functions_t functions;
        structs_t structs;
    } prj_t;

#endif