from chardet.universaldetector import UniversalDetector
import argparse

#需要安装模块 chardet

def detect_file_content(file_name):
    """
    判断文件的编码形式
    """
    detector = UniversalDetector()

    with open(file_name, 'rb') as f:
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
    detector.close()

    return detector.result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = 'codedetect', description = '获取文件的编码')
    parser.add_argument('file_name')
    namespace = parser.parse_args()

    print(detect_file_content(namespace.file_name))