cmake_minimum_required(VERSION 3.2)
project(main)

# Find Protobuf package
find_package(Protobuf REQUIRED)


set(PROTO_FILES ${CMAKE_SOURCE_DIR}/../utils/Messages.proto)

# Generate Protobuf C++ sources
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${CMAKE_SOURCE_DIR}/../utils/Messages.proto)

# Find the package using pkg-config
find_package(PkgConfig REQUIRED)
pkg_check_modules(CARIBOULITE REQUIRED cariboulite)

# Set C++ standard and pthread flag
set(CMAKE_CXX_STANDARD 11)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
# Include the utils directory for header files
include_directories(${CMAKE_SOURCE_DIR}/../utils)
set(UTILS_SOURCES
    ${CMAKE_SOURCE_DIR}/../utils/External.cpp
    ${CMAKE_SOURCE_DIR}/../utils/UDPcommunicator.cpp
    ${CMAKE_SOURCE_DIR}/../utils/ProtobufTransformer.cpp
    ${CMAKE_SOURCE_DIR}/../utils/SignalRx.cpp
)

# Add the executable
add_executable(main main.cpp RxMeas.cpp ${PROTO_SRCS} ${PROTO_HDRS} ${UTILS_SOURCES})

# Include directories from the cariboulite package
target_include_directories(main PRIVATE ${CARIBOULITE_INCLUDE_DIRS})

# Link against the cariboulite library and Protobuf
target_link_libraries(main PRIVATE ${CARIBOULITE_LIBRARIES} ${PROTOBUF_LIBRARIES} -lcariboulite)