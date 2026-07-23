class ImageEncoder:
    @staticmethod
    def encode(image):
        return {
            "image": image.tolist()
        }

    @staticmethod
    def decode(response):
        return response