import os
import torch
from configs import Config
from transformers import TrOCRProcessor, VisionEncoderDecoderModel


class TEXT_RECOGNITION:
    processor = None
    device = None
    model = None

    def __init__(self) -> None:
        """
        #### Class constructor for initializing the OCRRecognizer object.
        """
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.processor = TrOCRProcessor.from_pretrained(os.path.join(
            Config.ROOT_DIR.value, 'RECOGNITION', 'model', 'handwritten_best'))
        self.model = VisionEncoderDecoderModel.from_pretrained(os.path.join(
            Config.ROOT_DIR.value, 'RECOGNITION', 'model', 'handwritten_best')).to(self.device)

    def recognize(self, image) -> str:
        """
        #### A method to recognize text in an input image using the initialized OCRRecognizer object.

        Arguments:
        - image: A PIL.Image object or a NumPy array that represents the input image to be recognized.

        Returns:
        - generated_text: A string containing the recognized text in the input image.
        """
        img = image
        pixel_values = self.processor(
            images=img, return_tensors="pt", device=self.device).pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True)[0]
        return generated_text
