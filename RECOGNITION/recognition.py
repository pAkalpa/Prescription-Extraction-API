import os
import torch
from configs import Config
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from error import RecognitionInitializationError, RecognitionRecognizeError


class TEXT_RECOGNITION:
    processor = None
    device = None
    model = None

    def __init__(self) -> None:
        """
        #### Initializes the OCR model for recognizing handwritten text from images.

        Attributes:
        - device: An instance of the torch.device class, representing the hardware accelerator (GPU or CPU) available for running the model.
        - processor: An instance of the TrOCRProcessor class, which performs text normalization and post-processing on the OCR output.
        - model: An instance of the VisionEncoderDecoderModel class, representing the pre-trained OCR model loaded from disk.

        Arguments:
        - None

        Raises:
        - RecognitionInitializationError: If an error occurs while loading the OCR model, such as a missing or corrupted file, unsupported file format, or incorrect file path.

        Notes:
        - This function initializes the OCR model by loading the pre-trained model weights and associated processing components from disk. The paths to these files are specified in the `Config` object.
        - The `device` attribute is set to the available GPU device if one is available, or to the CPU if not.
        - The initialized OCR model can be used to recognize handwritten text from images by calling the `recognize()` method of the object, which takes an image file or array as input and returns the recognized text as a string.

        """
        try:
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu")
            self.processor = TrOCRProcessor.from_pretrained(os.path.join(
                Config.ROOT_DIR.value, 'RECOGNITION', 'model', 'handwritten_best'))
            self.model = VisionEncoderDecoderModel.from_pretrained(os.path.join(
                Config.ROOT_DIR.value, 'RECOGNITION', 'model', 'handwritten_best')).to(self.device)
        except:
            raise RecognitionInitializationError()

    def recognize(self, image) -> str:
        """
        #### Recognizes handwritten text from an input image using the initialized OCR model.

        Arguments:
        - image: A PIL image object or NumPy array representing the input image to be recognized.

        Returns:
        - recognized_text (str): A string containing the recognized text extracted from the input image.

        Raises:
        - RecognitionRecognizeError: If an error occurs while recognizing the text, such as an issue with the input image or the OCR model.

        Notes:
        - This function preprocesses the input image using the TrOCRProcessor object to normalize and prepare the image for OCR.
        - The processed image is then passed through the OCR model to generate a sequence of predicted token IDs, which are decoded back into a string of text using the TrOCRProcessor object.
        - The recognized text is returned as a string.
        - If an error occurs during any step of the OCR process, a custom exception, `RecognitionRecognizeError`, is raised.

        """
        try:
            img = image
            pixel_values = self.processor(
                images=img, return_tensors="pt", device=self.device).pixel_values.to(self.device)
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(
                generated_ids, skip_special_tokens=True)[0]
            return generated_text
        except:
            raise RecognitionRecognizeError()
