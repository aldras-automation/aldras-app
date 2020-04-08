// This provides the frozen (compiled bytecode) files that are included if
// any.
#include <Python.h>

#include "nuitka/constants_blob.h"

// Blob from which modules are unstreamed.
#define stream_data constant_bin

// These modules should be loaded as bytecode. They may e.g. have to be loadable
// during "Py_Initialize" already, or for irrelevance, they are only included
// in this un-optimized form. These are not compiled by Nuitka, and therefore
// are not accelerated at all, merely bundled with the binary or module, so
// that CPython library can start out finding them.

struct frozen_desc {
    char const *name;
    ssize_t start;
    int size;
};

void copyFrozenModulesTo( struct _frozen *destination )
{
    struct frozen_desc frozen_modules[] = {
        {"_collections_abc", 6202633, 28953},
        {"_compression", 6231586, 4135},
        {"_weakrefset", 6235721, 7473},
        {"abc", 6243194, 6462},
        {"base64", 6249656, 17001},
        {"bz2", 6266657, 11192},
        {"codecs", 6277849, 34127},
        {"collections", 6311976, -47103},
        {"collections.abc", 6202633, 28953},
        {"copyreg", 6359079, 4255},
        {"dis", 6363334, 15216},
        {"encodings", 6378550, -3958},
        {"encodings.aliases", 6382508, 6307},
        {"encodings.ascii", 6388815, 1895},
        {"encodings.base64_codec", 6390710, 2434},
        {"encodings.big5", 6393144, 1455},
        {"encodings.big5hkscs", 6394599, 1465},
        {"encodings.bz2_codec", 6396064, 3296},
        {"encodings.charmap", 6399360, 2948},
        {"encodings.cp037", 6402308, 2440},
        {"encodings.cp1006", 6404748, 2516},
        {"encodings.cp1026", 6407264, 2444},
        {"encodings.cp1125", 6409708, 8137},
        {"encodings.cp1140", 6417845, 2430},
        {"encodings.cp1250", 6420275, 2467},
        {"encodings.cp1251", 6422742, 2464},
        {"encodings.cp1252", 6425206, 2467},
        {"encodings.cp1253", 6427673, 2480},
        {"encodings.cp1254", 6430153, 2469},
        {"encodings.cp1255", 6432622, 2488},
        {"encodings.cp1256", 6435110, 2466},
        {"encodings.cp1257", 6437576, 2474},
        {"encodings.cp1258", 6440050, 2472},
        {"encodings.cp273", 6442522, 2426},
        {"encodings.cp424", 6444948, 2470},
        {"encodings.cp437", 6447418, 7854},
        {"encodings.cp500", 6455272, 2440},
        {"encodings.cp65001", 6457712, 1694},
        {"encodings.cp720", 6459406, 2537},
        {"encodings.cp737", 6461943, 8176},
        {"encodings.cp775", 6470119, 7884},
        {"encodings.cp850", 6478003, 7515},
        {"encodings.cp852", 6485518, 7892},
        {"encodings.cp855", 6493410, 8145},
        {"encodings.cp856", 6501555, 2502},
        {"encodings.cp857", 6504057, 7497},
        {"encodings.cp858", 6511554, 7485},
        {"encodings.cp860", 6519039, 7833},
        {"encodings.cp861", 6526872, 7848},
        {"encodings.cp862", 6534720, 8037},
        {"encodings.cp863", 6542757, 7848},
        {"encodings.cp864", 6550605, 7994},
        {"encodings.cp865", 6558599, 7848},
        {"encodings.cp866", 6566447, 8181},
        {"encodings.cp869", 6574628, 7874},
        {"encodings.cp874", 6582502, 2568},
        {"encodings.cp875", 6585070, 2437},
        {"encodings.cp932", 6587507, 1457},
        {"encodings.cp949", 6588964, 1457},
        {"encodings.cp950", 6590421, 1457},
        {"encodings.euc_jis_2004", 6591878, 1471},
        {"encodings.euc_jisx0213", 6593349, 1471},
        {"encodings.euc_jp", 6594820, 1459},
        {"encodings.euc_kr", 6596279, 1459},
        {"encodings.gb18030", 6597738, 1461},
        {"encodings.gb2312", 6599199, 1459},
        {"encodings.gbk", 6600658, 1453},
        {"encodings.hex_codec", 6602111, 2421},
        {"encodings.hp_roman8", 6604532, 2641},
        {"encodings.hz", 6607173, 1451},
        {"encodings.idna", 6608624, 5735},
        {"encodings.iso2022_jp", 6614359, 1472},
        {"encodings.iso2022_jp_1", 6615831, 1476},
        {"encodings.iso2022_jp_2", 6617307, 1476},
        {"encodings.iso2022_jp_2004", 6618783, 1482},
        {"encodings.iso2022_jp_3", 6620265, 1476},
        {"encodings.iso2022_jp_ext", 6621741, 1480},
        {"encodings.iso2022_kr", 6623221, 1472},
        {"encodings.iso8859_1", 6624693, 2439},
        {"encodings.iso8859_10", 6627132, 2444},
        {"encodings.iso8859_11", 6629576, 2538},
        {"encodings.iso8859_13", 6632114, 2447},
        {"encodings.iso8859_14", 6634561, 2465},
        {"encodings.iso8859_15", 6637026, 2444},
        {"encodings.iso8859_16", 6639470, 2446},
        {"encodings.iso8859_2", 6641916, 2439},
        {"encodings.iso8859_3", 6644355, 2446},
        {"encodings.iso8859_4", 6646801, 2439},
        {"encodings.iso8859_5", 6649240, 2440},
        {"encodings.iso8859_6", 6651680, 2484},
        {"encodings.iso8859_7", 6654164, 2447},
        {"encodings.iso8859_8", 6656611, 2478},
        {"encodings.iso8859_9", 6659089, 2439},
        {"encodings.johab", 6661528, 1457},
        {"encodings.koi8_r", 6662985, 2491},
        {"encodings.koi8_t", 6665476, 2402},
        {"encodings.koi8_u", 6667878, 2477},
        {"encodings.kz1048", 6670355, 2454},
        {"encodings.latin_1", 6672809, 1907},
        {"encodings.mac_arabic", 6674716, 7748},
        {"encodings.mac_centeuro", 6682464, 2478},
        {"encodings.mac_croatian", 6684942, 2486},
        {"encodings.mac_cyrillic", 6687428, 2476},
        {"encodings.mac_farsi", 6689904, 2420},
        {"encodings.mac_greek", 6692324, 2460},
        {"encodings.mac_iceland", 6694784, 2479},
        {"encodings.mac_latin2", 6697263, 2620},
        {"encodings.mac_roman", 6699883, 2477},
        {"encodings.mac_romanian", 6702360, 2487},
        {"encodings.mac_turkish", 6704847, 2480},
        {"encodings.mbcs", 6707327, 1706},
        {"encodings.oem", 6709033, 1519},
        {"encodings.palmos", 6710552, 2467},
        {"encodings.ptcp154", 6713019, 2561},
        {"encodings.punycode", 6715580, 6432},
        {"encodings.quopri_codec", 6722012, 2454},
        {"encodings.raw_unicode_escape", 6724466, 1780},
        {"encodings.rot_13", 6726246, 3040},
        {"encodings.shift_jis", 6729286, 1465},
        {"encodings.shift_jis_2004", 6730751, 1475},
        {"encodings.shift_jisx0213", 6732226, 1475},
        {"encodings.tis_620", 6733701, 2529},
        {"encodings.undefined", 6736230, 2174},
        {"encodings.unicode_escape", 6738404, 1760},
        {"encodings.unicode_internal", 6740164, 1770},
        {"encodings.utf_16", 6741934, 4844},
        {"encodings.utf_16_be", 6746778, 1645},
        {"encodings.utf_16_le", 6748423, 1645},
        {"encodings.utf_32", 6750068, 4737},
        {"encodings.utf_32_be", 6754805, 1538},
        {"encodings.utf_32_le", 6756343, 1538},
        {"encodings.utf_7", 6757881, 1566},
        {"encodings.utf_8", 6759447, 1625},
        {"encodings.utf_8_sig", 6761072, 4527},
        {"encodings.uu_codec", 6765599, 3287},
        {"encodings.zlib_codec", 6768886, 3134},
        {"enum", 6772020, 24281},
        {"functools", 6796301, 24242},
        {"genericpath", 6820543, 3915},
        {"heapq", 6824458, 14373},
        {"importlib", 6838831, -3743},
        {"importlib._bootstrap", 6842574, 29189},
        {"importlib._bootstrap_external", 6871763, 41829},
        {"importlib.machinery", 6913592, 983},
        {"inspect", 6914575, 80054},
        {"io", 6994629, 3420},
        {"keyword", 6998049, 1820},
        {"linecache", 6999869, 3800},
        {"locale", 7003669, 34599},
        {"ntpath", 7038268, 13015},
        {"opcode", 7051283, 5389},
        {"operator", 7056672, 13911},
        {"os", 7070583, 29809},
        {"quopri", 7100392, 5782},
        {"re", 7106174, 13815},
        {"reprlib", 7119989, 5361},
        {"sre_compile", 7125350, 15214},
        {"sre_constants", 7140564, 6302},
        {"sre_parse", 7146866, 21297},
        {"stat", 7168163, 4355},
        {"stringprep", 7172518, 10043},
        {"struct", 7182561, 345},
        {"threading", 7182906, 37897},
        {"token", 7220803, 3610},
        {"tokenize", 7224413, 17842},
        {"traceback", 7242255, 19634},
        {"types", 7261889, 8987},
        {"warnings", 7270876, 13847},
        {NULL, 0, 0}
    };

    struct frozen_desc *current = frozen_modules;

    for(;;)
    {
        destination->name = (char *)current->name;
        destination->code = (unsigned char *)&constant_bin[ current->start ];
        destination->size = current->size;

        if (destination->name == NULL) break;

        current += 1;
        destination += 1;
    };
}
