import logging
from flask import Blueprint, render_template, current_app, jsonify, request, redirect, flash


# Create the blueprint and give it a unique name
whatsapp = Blueprint('whatsapp', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detailed logs
logger = logging.getLogger(__name__)
            

@whatsapp.route('/setup_whatsapp', methods=['GET', 'POST'])
def setup_whatsapp():
    return render_template('whatsapp.html')
