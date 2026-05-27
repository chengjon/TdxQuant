#ifndef __PLUGIN_TCALC_FUNC
#define __PLUGIN_TCALC_FUNC

#pragma pack(push, 1)

// Function signature: (data count, output, input a, input b, input c).
typedef void (*pPluginFUNC)(int, float*, float*, float*, float*);

typedef struct tagPluginTCalcFuncInfo
{
    unsigned short nFuncMark; // Function mark/id.
    pPluginFUNC pCallFunc;    // Function address.
} PluginTCalcFuncInfo;

typedef BOOL (*pRegisterPluginFUNC)(PluginTCalcFuncInfo**);

#pragma pack(pop)

#endif
