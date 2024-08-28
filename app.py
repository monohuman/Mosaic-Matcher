import numpy as np
from PIL import Image
import sys, os, random, string, asyncio, csv, time

def get_mean_color(image):
    ''' Calculate the mean color of each image and return as a RGB color '''
    image = image.convert("RGB")
    image_array = np.array(image)
    mean_color = tuple(np.mean(image_array.reshape(-1, 3), axis=0).astype(int))
    return mean_color

def load_images(directory, dataset_name):
    ''' Load images from the dataset directory and return a list of tuples containing the filename, mean color, and image '''
    images = []
    csv_file_path = f"{dataset_name}.csv"
    
    # The csv file contains the filename and mean color of each image from the dataset
    if os.path.exists(csv_file_path):
        print(f"CSV file '{csv_file_path}' already exists. Loading images from CSV.\n")
        with open(csv_file_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                # For each image, get the filename, mean color, and image
                filename = row[0]
                mean_color = tuple(map(int, row[1].strip('()').split(',')))
                img_path = os.path.join(directory, filename)
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    images.append((filename, mean_color, image))
                else:
                    print(f"Image file {img_path} not found. Skipping.")
    else:
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Filename', 'Mean Color'])
            
            file_count = len(os.listdir(directory))
            processed_files = 0
            
            for filename in os.listdir(directory):
                # If the csv file doesn't exist, calculate the mean color of each image and save it to the dataset's csv file
                if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                    img_path = os.path.join(directory, filename)
                    image = Image.open(img_path)
                    mean_color = get_mean_color(image)
                    images.append((filename, mean_color, image))
                    writer.writerow([filename, mean_color])
                    
                    # Pretty cool progress bar if I do say so myself (again)
                    processed_files += 1
                    progress = processed_files / file_count * 100
                    sys.stdout.write("\rLoading images: |")
                    for i in range(25):
                        if i < progress // 4:
                            sys.stdout.write("█")
                        else:
                            sys.stdout.write("-")
                    sys.stdout.write("| {0:.2f}%  ".format(progress))
                    sys.stdout.flush()
    
    return images

def find_closest_image(target_color, images):
    ''' Find the image with the closest mean color to the target color. '''
    if not images:
        raise ValueError("The images list is empty.")
        
    def color_distance(c1, c2):
        ''' Calculate the Euclidean distance between two RGB colors. '''
        return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

    closest_image = min(images, key=lambda img: color_distance(target_color, img[1]))
    return closest_image[2]

async def process_image(input_image_path, output_image_path, images, block_size):
    '''Process the input image and save the output image.'''
    input_image = Image.open(input_image_path)
    input_image = input_image.convert("RGB")  # Make sure the input image is in RGB colorspace
    output_image = Image.new('RGB', input_image.size)
    
    width, height = input_image.size
    
    total_blocks = (width // block_size) * (height // block_size)
    processed_blocks = 0
    start_time = time.time()
    
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # For each block (x * y) in the input image, find the closest image from the dataset and paste it into the output image

            box = (x, y, x + block_size, y + block_size) # (left, upper, right, lower)
            block = input_image.crop(box) # Crop the block from the input image
            mean_color = get_mean_color(block) # Calculate the mean color of the block
            closest_image = find_closest_image(mean_color, images) # Find the closest image from the dataset
            resized_image = closest_image.resize((block_size, block_size)) # Resize the closest image to the block size
            output_image.paste(resized_image, box) # Paste the resized image into the output image
            
            processed_blocks += 1
            progress = processed_blocks / total_blocks * 100
            elapsed_time = time.time() - start_time
            percent_per_second = progress / elapsed_time
            remaining_time = (100 - progress) / (progress / elapsed_time)

            # Pretty cool progress bar if I do say so myself
            sys.stdout.write("\rProgress: |")
            for i in range(25):
                if i < progress // 4:
                    sys.stdout.write("█")
                else:
                    sys.stdout.write("-")
            sys.stdout.write("| {0:.2f}%  ".format(progress))
            sys.stdout.write("({0:.2f}% per second)  ".format(percent_per_second))
            if remaining_time < 60:
                sys.stdout.write("Remaining time: {0:.0f}s  ".format(remaining_time))
            else:
                minutes, seconds = divmod(remaining_time, 60)
                sys.stdout.write("Remaining time: {0:.0f}m{1:.0f}s  ".format(minutes, seconds))
            sys.stdout.flush()
    
    output_image.save(output_image_path)

async def process_images(input_image_folder, images_directory, output_directory, block_size, dataset):
    ''' Process all images in the input folder and save the outputs to the output folder. '''
    images = load_images(images_directory, dataset)
    if not images:
        print("No images loaded. Exiting.")
        return
    
    tasks = []
    
    for filename in os.listdir(input_image_folder):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            # This is to make sure the output image has a unique name and is doesnt overwrite any existing images
            random_name = ''.join(random.choices(string.ascii_lowercase, k=5))
            input_image_path = os.path.join(input_image_folder, filename)
            output_image_path = os.path.join(output_directory, f'{random_name}.jpg')
            print(f'Processing image: {input_image_path}')
            task = asyncio.create_task(process_image(input_image_path, output_image_path, images, block_size))
            tasks.append(task)
    
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # The name of the dataset folder containing the images to use for the mosaic
    dataset = input('\nEnter dataset name: ')

    # The smaller the block size, the more detailed the output image will be (and the longer it will take to process)
    block_size = int(input('Enter block size (default is 5): ') or 5)

    input_directory = 'inputs'
    output_directory = 'outputs'
    images_directory = f'datasets/{dataset}'

    if not os.path.exists(images_directory):
        print(f"Dataset '{dataset}' does not exist. Exiting.\n")
        sys.exit(1)

    asyncio.run(process_images(input_directory, images_directory, output_directory, block_size, dataset))

# Just a lil note here that you can create a dataset full of pictures of yourself, and then make a picture of yourself out of mini pictures of yourself
# I did this and the result was pretty cool!