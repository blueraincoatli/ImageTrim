from PIL import Image, UnidentifiedImageError
import os
import pillow_avif  # 确保 AVIF 插件被注册

def convert_to_avif(input_path, output_path):
    try:
        img = Image.open(input_path)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')
        img.save(output_path, "AVIF", quality=85)
        print(f'转换完成：{input_path} -> {output_path}')
    except FileNotFoundError:
        print(f'错误：输入文件未找到 {input_path}')
    except UnidentifiedImageError:
        print(f'错误：无法识别的图片格式 {input_path}')
    except ImportError:
        print(f'错误：缺少必要的库来处理 AVIF。请确保已安装 "pillow-avif-plugin"。')
    except OSError as e:
        print(f'处理文件 {input_path} 时 Pillow 保存出错: {e}')
        if "encoder error" in str(e).lower() or "decoder error" in str(e).lower():
            print(f'这可能表示缺少 AVIF 编解码器 (如 libavif) 或插件未正确加载。')
        if "cannot write mode" in str(e).lower():
            print(f'图片模式 {img.mode} 可能不被 AVIF 直接支持，尝试转换模式。')
    except Exception as e:
        print(f'处理文件 {input_path} 时发生未知错误: {e}')

def ensure_unique_filename(output_path):
    """确保输出文件名唯一，如果文件已存在则添加数字后缀"""
    if not os.path.exists(output_path):
        return output_path
    base_path, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(f"{base_path}_{counter}{ext}"):
        counter += 1
    return f"{base_path}_{counter}{ext}"

# 获取脚本当前目录
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
input_dir = script_dir

current_folder_name = os.path.basename(script_dir)
parent_dir = os.path.dirname(script_dir)
if not current_folder_name:
    current_folder_name = os.path.basename(os.path.normpath(script_dir))
output_folder_name = f"{current_folder_name}_avif"
absolute_output_dir = os.path.join(parent_dir, output_folder_name)

if not os.path.exists(absolute_output_dir):
    try:
        os.makedirs(absolute_output_dir)
        print(f'创建输出目录：{absolute_output_dir}')
    except Exception as e:
        print(f'创建输出目录 {absolute_output_dir} 失败: {e}')
        exit()

if not os.path.isdir(input_dir):
    print(f"错误：输入目录 '{input_dir}' 不存在或不是一个目录。")
    exit()

print(f'开始从目录 {input_dir} 递归转换图片到 {absolute_output_dir}...')
converted_count = 0
failed_count = 0
processed_dirs = 0

for root, dirs, files in os.walk(input_dir):
    rel_path = os.path.relpath(root, input_dir)
    if rel_path == '.':
        current_output_dir = absolute_output_dir
    else:
        current_output_dir = os.path.join(absolute_output_dir, rel_path)
        if not os.path.exists(current_output_dir):
            try:
                os.makedirs(current_output_dir)
                print(f'创建子目录：{current_output_dir}')
            except Exception as e:
                print(f'创建子目录 {current_output_dir} 失败: {e}')
                continue

    if rel_path != '.':
        print(f'\n处理目录: {root}')
    processed_dirs += 1

    dir_file_count = 0
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            input_file = os.path.join(root, filename)
            output_filename = f'{os.path.splitext(filename)[0]}.avif'
            output_file = os.path.join(current_output_dir, output_filename)
            output_file = ensure_unique_filename(output_file)
            print(f'  正在处理: {filename}')
            try:
                convert_to_avif(input_file, output_file)
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    converted_count += 1
                    dir_file_count += 1
                else:
                    print(f'  警告: {output_file} 未成功创建或为空。')
                    failed_count += 1
            except Exception as e:
                print(f'  调用 convert_to_avif 处理 {input_file} 时出错: {e}')
                failed_count += 1
        else:
            if filename.lower().endswith(('.gif', '.bmp', '.tiff', '.webp')):
                print(f'  跳过非支持格式: {filename}')

    if dir_file_count > 0:
        print(f'  本目录转换了 {dir_file_count} 个文件')

print(f'\n所有指定图片处理完成！')
print(f'总共处理了 {processed_dirs} 个目录')
print(f'成功转换: {converted_count} 个文件')
print(f'转换失败: {failed_count} 个文件')
input("\n处理完成，按 Enter 键退出...")
