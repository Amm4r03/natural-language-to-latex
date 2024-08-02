from pdf2image import convert_from_path
import os
from PIL import Image, ImageChops
import cohere
import json
from dotenv import load_dotenv

def latex_to_jpg(equation : str, user_prompt : str) : 
    user_prompt = user_prompt.strip()
    
    # im trying to figure out how to fix this issue rn
    article = r"{article}"
    amsmath = r"{amsmath}"
    document = r"{document}"
    center = r"{center}"
    gobble = r"{gobble}"
    sixty = r"{60}"
    fifty = r"{50}"
    
    template2 = rf"""
    \documentclass{{article}}
    \usepackage{{amsmath}}
    \pagenumbering{gobble}
    \begin{document}
    \vfill
    \begin{center}
    \[
    {equation}
    \]
    \end{center}
    \vfill
    \end{document}
    """

    file_name = "equation.tex"

    with open(file_name, "w") as file:
        file.write(template2)

    os.system(f"pdflatex -interaction=nonstopmode -quiet {file_name}")

    def crop_image_to_equation(image):
        # Convert image to grayscale
        gray_image = image.convert('L')

        # Invert the grayscale image to make the equation white on black background
        inverted_image = ImageChops.invert(gray_image)
        
        # gray_image.save("gray_image.jpg")
        # inverted_image.save("inverted_image.jpg")

        # Get the bounding box of the non-zero regions
        bbox = inverted_image.getbbox()

        # print(f"Bounding box: {bbox}")
        new_bb = []
        border = 20
        for index, x in enumerate(bbox):
            if index <= 1:
                new_bb.append(x - border)
            else:
                new_bb.append(x + border)
        
        new_bbox = tuple(new_bb)
        # print(f"updated bounding box : {new_bbox}")

        # Crop the image to the bounding box
        # if bbox:
        cropped_image = image.crop(new_bbox)
        print("rendered image successfully")
        return cropped_image
        # return image

    pdf_path = "equation.pdf"
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images = convert_from_path(pdf_path, dpi=600)

    for i, image in enumerate(images):
        cropped_image = crop_image_to_equation(image)
        image_path = os.path.join(output_dir, f'{user_prompt}_{i + 1}.jpg')
        cropped_image.save(image_path, 'JPEG')


# define your equation latex here
# equation = r"k_1 \times k_i = \alpha^{\pi}"
# equation = r"F = G \frac{m_1 \times m_2}{r^2}"
# equation = r"f(x) = 37x^{3} + 27x^{2}+5"
# equation = r"f(x) = \frac{1}{\sigma \sqrt{2 \pi} e^{-\frac{1}{2} \left(\frac{x - \mu}{\sigma} \right) ^ 2}}"

# equation = r"\iiint \frac{\partial F_3}{\partial x} dV = I_{\text{test}}"
# equation = r"\frac{\partial ^2}{\partial x^2} \psi (x,t) + \frac{\partial ^2}{\partial z^2} \psi (x,y,t) - \frac{\partial }{\partial x}V\psi (x,y,z,t) = -i\hbar \frac{\partial \psi (x,y,z,t)}{\partial t}"

def getLatex() -> str :
    load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    co = cohere.Client(cohere_api_key)
    user_equation = input("enter an expression or a mathematical statement : ")

    instruction = r"""
    For any given mathematical expression or theorem, return only the LaTeX code for the equation, and nothing else.
    No plaintext, explanations, or any other text should be included in your response
    
    Example:
    User: integrate x from -2 to 5
    Output: \int_{-2}^{5} x
    
    user equation : 
    """

    prompt = instruction + user_equation

    response = co.chat(
        message=prompt,
        model="command"
    )
    
    response = response.json()
    # print(response)
    data = json.loads(response)
    resp = data["text"]
    # print(resp)
    a = str(response)
    # print(response, end="\n\n")
    # final_response = a[5:a[9::].find("\"") + 10]
    # print(f"bot response : {final_response}")
    return [resp, user_equation]

eq = getLatex()
equation = eq[0]
# print(f"equation received : {equation}")
prohibited_words = ["\"", "$", "`"]
for w in prohibited_words:
    equation = equation.replace(w, "")
# print(equation)

file_name = eq[1].replace("^", "")
file_name_prohibited = ["^", ",", "<", ">", "$", ";"]

for w in file_name_prohibited:
    file_name = file_name.replace(w, "")

file_name = file_name.replace(" ", "_").strip()

print(f"final equation : {equation}")
print(f"file name : {file_name}")

latex_to_jpg(equation, file_name)

file_name += "_1.jpg"

os.system(f"start output/{file_name}")