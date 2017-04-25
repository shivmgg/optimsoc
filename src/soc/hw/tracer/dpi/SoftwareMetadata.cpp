#include "Tracer.h"

const std::string Tracer::mSoftwareMetadata =
        "/* CTF 1.8 */\n\n"
        "typealias integer {\n"
        "  size = 64;\n"
        "  signed = false;\n"
        "  align = 8;\n"
        "} := uint64_t;\n"
        "\n"
        "typealias integer {\n"
        "  size = 32;\n"
        "  signed = false;\n"
        "  align = 8;\n"
        "} := uint32_t;\n"
        "\n"
        "typealias integer {\n"
        "    size = 16;\n"
        "    signed = false;\n"
        "    align = 8;\n"
        "} := uint16_t;\n"
        "\n"
        "typealias integer {\n"
        "    size = 8;\n"
        "    signed = false;\n"
        "    align = 8;\n"
        "} := uint8_t;\n"
        "\n"
        "trace {\n"
        "    major = 1;\n"
        "    minor = 8;\n"
        "    byte_order = le;\n"
        "};\n"
        "\n"
        "stream {\n"
        "    event.header := struct {\n"
        "        uint64_t timestamp;\n"
        "        uint16_t id;\n"
        "    };\n"
        "    event.context := struct {\n"
        "        uint16_t cpu_id;\n"
        "    };\n"
        "};\n"
        "\n"
        "event {\n"
        "    id = 0;\n"
        "    name = 'event';\n"
        "    fields := struct {\n"
        "        uint16_t id;\n"
        "        uint32_t value;\n"
        "    };\n"
        "};\n";
