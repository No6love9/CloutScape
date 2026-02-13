"""
WebSocket events for real-time updates
"""
from flask_socketio import emit, join_room, leave_room


def register_socketio_events(socketio):
    """Register SocketIO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print('Client connected')
        emit('connected', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected')
    
    @socketio.on('join_price_updates')
    def handle_join_price_updates():
        """Join price updates room"""
        join_room('price_updates')
        emit('joined', {'room': 'price_updates'})
    
    @socketio.on('leave_price_updates')
    def handle_leave_price_updates():
        """Leave price updates room"""
        leave_room('price_updates')
        emit('left', {'room': 'price_updates'})


def broadcast_price_update(socketio, price_data):
    """Broadcast price update to all connected clients"""
    socketio.emit('price_update', price_data, room='price_updates')
