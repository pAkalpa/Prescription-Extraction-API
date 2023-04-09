class FileReadError(Exception):

    def __init__(self, message="INVALID MEDIA TYPE") -> None:
        self.message = message
        super().__init__(self.message)


class FirebaseInitializationError(Exception):

    def __init__(self, message="FIREBASE INITIALIZATION ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class FirebaseCreateDocumentError(Exception):

    def __init__(self, message="FIREBASE DOCUMENT CREATION ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class FirebaseUpdateDocumentError(Exception):

    def __init__(self, message="FIREBASE DOCUMENT UPDATE ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class FirebaseUploadError(Exception):

    def __init__(self, message="FIREBASE FILE UPLOAD ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class DetectionInitializationError(Exception):

    def __init__(self, message="DETECTION MODEL INITIALIZATION ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class DetectionDetectError(Exception):

    def __init__(self, message="DETECTION MODEL DETECT ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class DetectionCropError(Exception):

    def __init__(self, message="DETECTION MODEL CROP ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class RecognitionInitializationError(Exception):

    def __init__(self, message="RECOGNITION MODEL INITIALIZATION ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class RecognitionRecognizeError(Exception):

    def __init__(self, message="RECOGNITION MODEL RECOGNIZE ERROR") -> None:
        self.message = message
        super().__init__(self.message)
