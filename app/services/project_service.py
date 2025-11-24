from firebase_admin import firestore
from google.cloud.firestore import SERVER_TIMESTAMP
from app.models.project import ProjectDTO # Data Transfer Object
from typing import List, Optional

class ProjectService:
    """Service for managing projects with Firebase."""
    
    @staticmethod
    def _get_collection():
        """Get Firestore collection reference."""
        db = firestore.client()
        return db.collection('projects')

    @staticmethod
    def get_user_projects(user_id: str) -> List[dict]:
        """
        Fetches all projects owned by a specific user.
        """
        collection = ProjectService._get_collection()
        docs = collection.where('owner_id', '==', user_id).stream()
        
        projects = []
        for doc in docs:
            project_data = doc.to_dict()
            project_data['id'] = doc.id
            projects.append(project_data)
            
        return projects

    @staticmethod
    def create_project(data: dict) -> str:
        """
        Creates a new project.
        """
        collection = ProjectService._get_collection()
        
        new_doc = {
            'owner_id': data.get('author_id'),
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'created_at': SERVER_TIMESTAMP,
            'status': 'active'
        }
        
        update_time, doc_ref = collection.add(new_doc)
        return doc_ref.id

    @staticmethod
    def get_project(project_id: str) -> Optional[dict]:
        """
        Get a single project by ID.
        """
        collection = ProjectService._get_collection()
        doc_ref = collection.document(project_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        project_data = doc.to_dict()
        if project_data:
            project_data['id'] = doc.id
        return project_data
    
    @staticmethod
    def update_project(project_id: str, data: dict) -> bool:
        """
        Update an existing project.
        """
        collection = ProjectService._get_collection()
        doc_ref = collection.document(project_id)
        
        update_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'updated_at': SERVER_TIMESTAMP
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        doc_ref.update(update_data)
        return True
    
    @staticmethod
    def delete_project(project_id: str) -> bool:
        """
        Delete a project.
        """
        collection = ProjectService._get_collection()
        doc_ref = collection.document(project_id)
        doc_ref.delete()
        return True