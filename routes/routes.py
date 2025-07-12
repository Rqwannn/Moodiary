from controller.auth import Authentication
from controller.notes import NotesController
from controller.inference import InferenceModel

routes = [Authentication, NotesController, InferenceModel]