from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import TaxDocument, Receipt, User, db
import os
from werkzeug.utils import secure_filename

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    user_id = int(get_jwt_identity())
    documents = TaxTaxDocument.query.filter_by(user_id=user_id).all()
    return jsonify([doc.to_dict() for doc in documents]), 200

@documents_bp.route('/documents', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Create document record
        document = TaxDocument(
            user_id=user_id,
            file_path=file_path,
            document_type=request.form.get('document_type', 'other'),
            extracted_data={}  # OCR data will be added later
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
    
    return jsonify({'error': 'Invalid file type'}), 400

@documents_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    user_id = int(get_jwt_identity())
    document = TaxDocument.query.filter_by(id=document_id, user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document.to_dict()), 200

@documents_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    user_id = int(get_jwt_identity())
    document = TaxDocument.query.filter_by(id=document_id, user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Delete file from filesystem
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'message': 'Document deleted successfully'}), 200

@documents_bp.route('/receipts', methods=['GET'])
@jwt_required()
def get_receipts():
    user_id = int(get_jwt_identity())
    receipts = Receipt.query.filter_by(user_id=user_id).all()
    return jsonify([receipt.to_dict() for receipt in receipts]), 200

@documents_bp.route('/receipts', methods=['POST'])
@jwt_required()
def upload_receipt():
    user_id = int(get_jwt_identity())
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Create receipt record
        from datetime import date
        receipt = Receipt(
            user_id=user_id,
            file_path=file_path,
            category=request.form.get('category', 'general'),
            amount=float(request.form.get('amount', '0.00')),
            date=date.today()
        )
        
        db.session.add(receipt)
        db.session.commit()
        
        return jsonify({
            'message': 'Receipt uploaded successfully',
            'receipt': receipt.to_dict()
        }), 201
    
    return jsonify({'error': 'Invalid file type'}), 400
