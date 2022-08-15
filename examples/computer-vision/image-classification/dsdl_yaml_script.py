# -*-coding:utf-8-*-
import os.path
import sys
import json
import argparse
import re
from collections import defaultdict

# from pydantic import BaseModel
# from typing import Optional, List, Dict


TAB_SPACE = "    "


def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description="Convert v0.3 format to dsdl yaml file."
    )
    parser.add_argument(
        "-s" "--src_dir",
        dest="src_dir",
        help="source file path: eg./Users/jiangyiying/sherry/tunas_data_demo/MNIST-tunas",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-o" "--out_dir",
        dest="out_dir",
        default=None,
        help="out file path: eg./Users/jiangyiying/sherry/tunas_data_demo/MNIST-dsdl",
        type=str,
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(-1)

    args = parser.parse_args()
    return args


class ConvertV3toDsdlYaml:
    FIELD_MAPPING = {
        "int": "Int",
        "float": "Num",
        "str": "Str",
        "list": "List",
        "bool": "Bool",
    }

    def __init__(self, dataset_path, output_path=None):
        self.dataset_path = dataset_path
        self.output_path = output_path
        self.dataset_name = None
        self.struct_sample_name = None  # data里面的sample_type, 也是struct里面那个关键的Sample的名字
        self.dataset_info = dict()
        # 用来定义数据模型，就是.yaml的class_dom部分 {"name": struct_name: XXClassDom, "$def": struct_def, "classes":
        # dict_id_class, "param": param, "label": label}
        self.class_dom = dict()
        # 数据部分
        self.sample = dict()
        self.sub_dataset_name = None
        self.attributes = dict()  # {attribute_name: type}
        self.confidence = None  # confidence_type
        self.optional = set()

    @staticmethod
    def camel_case(s):
        s = s.replace("-", " ")
        s = re.sub(r"(_|- )+", " ", s).title().replace(" ", "")
        return s

    def get_dataset_info(self):
        file_name = os.path.join(self.dataset_path, "dataset_info.json")
        with open(file_name) as fp:
            dataset_info = json.load(fp)
        self.dataset_name = dataset_info["dataset_name"]
        self.struct_sample_name = self.camel_case(self.dataset_name) + "Sample"
        for task in dataset_info["tasks"]:
            if task["type"] == "classification":
                dict_id_class = {}
                struct_name = self.camel_case(task["name"]) + "ClassDom"
                struct_def = "class_domain"
                for c in task["catalog"]:
                    # 当类别名字是整数的时候生成yaml虽然没问题，但是yaml生成py文件的时候会有问题
                    # 因为py文件里面class中是不能出现变量名是int的，也不能是类似这样的字符串"0"（要是合法的str）
                    # 所以现在遇到这种情况我们统一将类别名变成'_XX'。。如MNIST数据集里面的类别是"0"，"1"。。会变成'_0'...
                    dict_id_class[c["category_id"]] = self.clean(c["category_name"])
                    supercategories = c.get("supercategories", None)
                    if supercategories:
                        supercategories = ".".join([self.clean(i) for i in supercategories])
                        dict_id_class[c["category_id"]] = self.clean(c["category_name"]) + "." + supercategories
                self.class_dom[task["name"]] = {
                    "name": struct_name,
                    "$def": struct_def,
                    "classes": dict_id_class,
                }
            else:
                continue

        if len(self.class_dom) == 1:
            self.class_dom[list(self.class_dom.keys())[0]]["param"] = "cdom"
            self.class_dom[list(self.class_dom.keys())[0]]["label"] = "label"
            self.optional.add("label")
        # 需要考虑有多个任务的情况，也就是不止一个分类任务，这时候参数也不只cdom一个。。我们分别命名为cdom1, cdom2...
        else:
            params = ["cdom" + str(i) for i in range(len(self.class_dom))]
            for name, param, i in zip(
                    self.class_dom, params, range(len(self.class_dom))
            ):
                label = "label" + str(i)
                # label_content = "Label[dom=" + param + "]"
                # fp.writelines(f"{TAB_SPACE * 2}{label}: {label_content}\n")
                self.class_dom[name]["param"] = param
                self.class_dom[name]["label"] = label
                self.optional.add(label)

    def get_sample_data(self, file_name):
        with open(file_name) as fp:
            dataset = json.load(fp)
        self.sub_dataset_name = dataset["sub_dataset_name"]
        self.samples = dataset["samples"]

    def write_class_yaml(self, out_file):
        with open(out_file, "w+") as fp:
            fp.writelines('$dsdl-version: "0.5.0"\n')
            fp.writelines("\n")
            for struct in self.class_dom.values():
                fp.writelines(f"{struct['name']}:\n")
                fp.writelines(f"{TAB_SPACE}$def: class_domain\n")
                fp.writelines(f"{TAB_SPACE}classes:\n")
                for class_name in struct["classes"].values():
                    fp.writelines(f"{TAB_SPACE * 2}- {class_name}\n")
                    # try:
                    #     int(class_name)
                    #     fp.writelines(
                    #         f"{TAB_SPACE * 2}- {self.dataset_name}_{class_name}\n"
                    #     )
                    # except ValueError:
                    #     fp.writelines(f"{TAB_SPACE*2}- {class_name}\n")
                fp.writelines("\n")

    def write_struct_yaml(self, out_file):
        with open(out_file, "w+") as fp:
            fp.writelines('$dsdl-version: "0.5.0"\n')
            fp.writelines("\n")
            fp.writelines(f"{self.struct_sample_name}:\n")
            fp.writelines(f"{TAB_SPACE}$def: struct\n")
            params = [i["param"] for i in self.class_dom.values()]
            fp.writelines(f"{TAB_SPACE}$params: {params}\n")
            # $field 部分
            fp.writelines(f"{TAB_SPACE}$fields: \n")
            fp.writelines(f"{TAB_SPACE * 2}image: Image\n")
            for sample_struct in self.class_dom.values():
                label = sample_struct["label"]
                label_content = "Label[dom=$" + sample_struct["param"] + "]"
                fp.writelines(f"{TAB_SPACE * 2}{label}: {label_content}\n")
            # if self.attributes:
            fp.writelines(f"{TAB_SPACE * 2}attributes: Dict\n")
            # for attr_name, attr_type in self.attributes.items():
            #     fp.writelines(
            #         f"{TAB_SPACE * 2}{attr_name}: {self.FIELD_MAPPING[attr_type]}\n"
            #     )
            # if self.confidence:
            fp.writelines(f"{TAB_SPACE * 2}confidence: Num\n")
            # $optional 部分
            fp.writelines(f"{TAB_SPACE}$optional: {list(self.optional)}\n")

    def write_data_yaml(self, import_file_list, out_file):
        """
        import_file_list: $import自段段导入文件
        """
        with open(out_file, "w+") as fp:
            fp.writelines('$dsdl-version: "0.5.0"\n')
            fp.writelines("$import:\n")
            for i in import_file_list:
                fp.writelines(f"{TAB_SPACE}- {i}\n")
            fp.writelines("\n")
            fp.writelines("meta:\n")
            fp.writelines(f'{TAB_SPACE}name: "{self.dataset_name}"\n')
            fp.writelines(f'{TAB_SPACE}creator: "MSRA"\n')
            fp.writelines(f'{TAB_SPACE}dataset-version: "1.0.0"\n')
            fp.writelines(f'{TAB_SPACE}subdata-name: "{self.sub_dataset_name}"\n')
            fp.writelines("\n")
            fp.writelines("data:\n")
            cdom_temp = [
                struct["param"] + "=" + struct["name"]
                for struct in self.class_dom.values()
            ]
            fp.writelines(
                f"{TAB_SPACE}sample-type: {self.struct_sample_name}[{','.join(cdom_temp)}]\n"
            )
            fp.writelines(f"{TAB_SPACE}samples:\n")
            for sample in self.samples:
                self.write_single_sample(sample, fp)

    def write_single_sample(self, sample, file_point):
        """提取sample信息，并格式化写入yaml文件
        sample = {
            'media': {'path':xxx, 'source':xxx, 'type':'image', 'height':xxx, 'width: xxx'},
            'ground_truth': [{
                "ann_id": str,
                "ref_ann_id": str,
                "name": str,
                "type": "classification",
                "source": str,
                "temporal_range": list[int or float],
                "temporal_unit": "frame_index" or "timestamp",
                "category_id": int,
                "confidence": float,
                "attributes": dict[str,any]
            },...]
        }
        """
        image_path = sample["media"]["path"]
        # eg. - image: "media/000000000007.png"
        file_point.writelines(f'{TAB_SPACE * 2}- image: "{image_path}"\n')

        if "ground_truth" in sample.keys():
            gts = sample["ground_truth"]
        else:
            gts = []

        for gt in gts:
            if gt["type"] == "classification":
                name = gt["name"]
                cls_id = gt["category_id"]
                cls_name = self.class_dom[name]["classes"][cls_id]
                label = self.class_dom[name]["label"]
                attributes = gt.get("attributes", None)
                confidence = gt.get("confidence", None)
                # eg. label: _9
                file_point.writelines(
                    f"{TAB_SPACE * 2}  {label}: {cls_name}\n"
                )
                # 这边还要考虑一个问题就是不同的task里面的attribute可能还不一样，目前是没有区分的，
                # 区分的话建议定义：self.attributes = defaultdict(dict), 然后其中的key是每个任务的名字，同self.class_dom
                if attributes:
                    file_point.writelines(
                        f"{TAB_SPACE * 2}  attributes: \n"
                    )
                    for attribute_name, attribute_value in attributes.items():
                        file_point.writelines(
                            f"{TAB_SPACE * 3}  {attribute_name}: {attribute_value}\n"
                        )
                        self.attributes.update(
                            {attribute_name: attribute_value.__class__.__name__}
                        )
                self.optional.add('attributes')
                if confidence:
                    file_point.writelines(
                        f"{TAB_SPACE * 2}  confidence: {confidence}\n"
                    )
                    self.confidence = confidence.__class__.__name__
                self.optional.add('confidence')

            else:
                pass

    def convert_pipeline(self):
        if not self.output_path:
            temp = os.path.basename(self.dataset_path)
            root_path = os.path.dirname(self.dataset_path)
            self.output_path = os.path.join(root_path, temp + "_dsdl")
            if not os.path.exists(self.output_path):
                os.mkdir(self.output_path)
        self.get_dataset_info()
        file_name = os.path.join(self.dataset_path, "annotations", "json")
        file_list = os.listdir(path=file_name)
        # 1. generate data yaml file
        import_file_list = ["class_dom", "struct_sample"]
        for file in file_list:
            self.get_sample_data(os.path.join(file_name, file))
            out_file = os.path.join(
                self.output_path, self.sub_dataset_name + "_data.yaml"
            )
            self.write_data_yaml(import_file_list, out_file)
            print(f"generate data yaml file: {out_file}")
        # 2. generate class yaml file
        out_file = os.path.join(self.output_path, "class-dom.yaml")
        self.write_class_yaml(out_file)
        print(f"generate class yaml file: {out_file}")
        # 3. generate struct sample yaml file
        out_file = os.path.join(self.output_path, "struct.yaml")
        self.write_struct_yaml(out_file)
        print(f"generate struct sample yaml file: {out_file}")

    @staticmethod
    def clean(varStr):
        return re.sub("\W|^(?=\d)", "_", varStr)


if __name__ == "__main__":
    args = parse_args()
    print(f"Called with args: \n{args}")
    src_file = args.src_dir
    out_file = args.out_dir
    print(f"your input source dictionary: {src_file}")
    print(f"your input destination dictionary: {out_file}")
    # src_file = "/Users/jiangyiying/sherry/tunas_data_demo/CIFAR100-tunas"
    # out_file = None
    v3toyaml = ConvertV3toDsdlYaml(src_file, out_file)
    v3toyaml.convert_pipeline()