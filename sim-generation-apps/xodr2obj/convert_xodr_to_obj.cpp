#include <iostream>
#include <fstream>
#include "OpenDriveMap.h"
#include "RoadNetworkMesh.h"

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input.xodr> <output.obj>" << std::endl;
        return 1;
    }

    std::string input_xodr = argv[1];
    std::string output_obj = argv[2];

    // OpenDRIVEファイルの読み込み
     odr::OpenDriveMap odr_map(input_xodr);

    if (odr_map.get_roads().empty()) {
        std::cerr << "Error: Failed to parse XODR file: " << input_xodr << std::endl;
        return 1;
    }

    std::cout << "Successfully loaded XODR file: " << input_xodr << std::endl;

    // 3D メッシュの生成
    odr::RoadNetworkMesh road_network_mesh = odr_map.get_road_network_mesh(0.1); // 0.1 はメッシュ精度

    // OBJファイルへ出力
    std::ofstream obj_file(output_obj);
    if (!obj_file) {
        std::cerr << "Error: Cannot write to file: " << output_obj << std::endl;
        return 1;
    }

    obj_file << road_network_mesh.get_mesh().get_obj();
    obj_file.close();

    std::cout << "OBJ file successfully written to: " << output_obj << std::endl;

    return 0;
}
