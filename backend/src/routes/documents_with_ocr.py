import os
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from src.models.user import TaxDocument, Receipt, User, db
from src.services.ocr_service import OCRService
from datetime import datetime

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/documents', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type', 'other')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Process document with OCR
        ocr_service = OCRService()
        ocr_result = ocr_service.process_tax_document(file_path, document_type)
        
        # Save document record with extracted data
        document = TaxDocument(
            user_id=user_id,
            document_type=document_type,
            file_path=f"uploads/documents/{filename}",
            extracted_data=ocr_result
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify(document.to_dict()), 201
    
    return jsonify({'error': 'Invalid file type'}), 400

@documents_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    user_id = int(get_jwt_identity())
    documents = TaxDocument.query.filter_by(user_id=user_id).all()
    return jsonify([doc.to_dict() for doc in documents]), 200

@documents_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    user_id = int(get_jwt_identity())
    document = TaxDocument.query.filter_by(id=document_id, user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document.to_dict()), 200

@documents_bp.route('/receipts', methods=['POST'])
@jwt_required()
def upload_receipt():
    user_id = int(get_jwt_identity())
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    category = request.form.get('category')
    amount = request.form.get('amount')
    date_str = request.form.get('date')
    
    if not amount or not date_str:
        return jsonify({'error': 'Amount and date are required'}), 400
    
    try:
        amount = float(amount)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid amount or date format'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'receipts')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Save receipt record
        receipt = Receipt(
            user_id=user_id,
            file_path=f"uploads/receipts/{filename}",
            category=category,
            amount=amount,
            date=date
        )
        
        db.session.add(receipt)
        db.session.commit()
        
        return jsonify(receipt.to_dict()), 201
    
    return jsonify({'error': 'Invalid file type'}), 400

@documents_bp.route('/receipts', methods=['GET'])
@jwt_required()
def get_receipts():
    user_id = int(get_jwt_identity())
    receipts = Receipt.query.filter_by(user_id=user_id).all()
    return jsonify([receipt.to_dict() for receipt in receipts]), 200

# CPA routes for accessing client documents
@documents_bp.route('/cpa/clients/<int:client_id>/documents', methods=['GET'])
@jwt_required()
def get_client_documents(client_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Check if current user is a CPA
    if not user or user.user_type != 'cpa':
        return jsonify({'error': 'Access denied'}), 403
    
    documents = TaxDocument.query.filter_by(user_id=client_id).all()
    return jsonify([doc.to_dict() for doc in documents]), 200

@documents_bp.route('/cpa/clients/<int:client_id>/receipts', methods=['GET'])
@jwt_required()
def get_client_receipts(client_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Check if current user is a CPA
    if not user or user.user_type != 'cpa':
        return jsonify({'error': 'Access denied'}), 403
    
    receipts = Receipt.query.filter_by(user_id=client_id).all()
    return jsonify([receipt.to_dict() for receipt in receipts]), 200
