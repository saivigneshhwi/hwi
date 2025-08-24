import React, { useState, useEffect } from 'react';
import { X, MapPin, Users, Clock, AlertTriangle, CheckCircle, Navigation, Phone, Mail } from 'lucide-react';
import MapView from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const TicketModal = ({ ticket, isOpen, onClose, onStatusUpdate }) => {
  const [status, setStatus] = useState(ticket.status);
  const [notes, setNotes] = useState(ticket.notes || '');
  const [view, setView] = useState('details'); // 'details' or 'map'

  const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example';

  const statusOptions = [
    { value: 'Pending', label: 'Pending', icon: Clock, color: 'bg-yellow-100 text-yellow-800' },
    { value: 'In Progress', label: 'In Progress', icon: AlertTriangle, color: 'bg-blue-100 text-blue-800' },
    { value: 'Done', label: 'Done', icon: CheckCircle, color: 'bg-green-100 text-green-800' },
    { value: 'Cancelled', label: 'Cancelled', icon: X, color: 'bg-gray-100 text-gray-800' }
  ];

  const getPriorityColor = (priority) => {
    const colors = {
      1: 'bg-gray-100 text-gray-700',
      2: 'bg-blue-100 text-blue-700',
      3: 'bg-yellow-100 text-yellow-700',
      4: 'bg-orange-100 text-orange-700',
      5: 'bg-red-100 text-red-700'
    };
    return colors[priority] || colors[1];
  };

  const handleStatusUpdate = () => {
    onStatusUpdate(ticket.id, status, notes);
  };

  const openInMaps = () => {
    const url = `https://www.google.com/maps?q=${ticket.latitude},${ticket.longitude}`;
    window.open(url, '_blank');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">SOS Request Details</h2>
              <p className="text-sm text-gray-500">ID: {ticket.external_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex h-[calc(90vh-120px)]">
          {/* Left Panel - Details */}
          <div className="w-1/2 p-6 overflow-y-auto">
            <div className="space-y-6">
              {/* Priority and Status */}
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(ticket.priority)}`}>
                  Priority {ticket.priority}
                </span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusOptions.find(s => s.value === ticket.status)?.color || 'bg-gray-100 text-gray-800'
                }`}>
                  {ticket.status}
                </span>
              </div>

              {/* Basic Info */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Emergency Details</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                      <span className="font-medium">{ticket.category}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-gray-500" />
                      <span>{ticket.place}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Users className="w-4 h-4 text-gray-500" />
                      <span>{ticket.people} people affected</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <span>Reported: {new Date(ticket.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                  <p className="text-gray-600 bg-gray-50 p-3 rounded-lg">
                    {ticket.text}
                  </p>
                </div>

                {/* Coordinates */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Location Coordinates</h4>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600">
                      Latitude: {ticket.latitude.toFixed(6)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Longitude: {ticket.longitude.toFixed(6)}
                    </p>
                    <button
                      onClick={openInMaps}
                      className="mt-2 flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm"
                    >
                      <Navigation className="w-4 h-4" />
                      <span>Open in Google Maps</span>
                    </button>
                  </div>
                </div>

                {/* Status Update */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Update Status</h4>
                  <div className="space-y-3">
                    <select
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {statusOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    
                    <textarea
                      placeholder="Add notes or comments..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    
                    <button
                      onClick={handleStatusUpdate}
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200"
                    >
                      Update Status
                    </button>
                  </div>
                </div>

                {/* Assignment */}
                {ticket.assigned_to && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Assigned To</h4>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-blue-800">{ticket.assigned_to}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Map */}
          <div className="w-1/2 border-l border-gray-200">
            <div className="h-full">
              <MapView
                mapboxAccessToken={MAPBOX_TOKEN}
                initialViewState={{
                  longitude: ticket.longitude,
                  latitude: ticket.latitude,
                  zoom: 12
                }}
                style={{ width: '100%', height: '100%' }}
                mapStyle="mapbox://styles/mapbox/streets-v11"
              >
                {/* SOS Location Marker */}
                <div
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 1
                  }}
                >
                  <div className="w-6 h-6 bg-red-500 rounded-full border-2 border-white shadow-lg animate-pulse"></div>
                </div>
              </MapView>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TicketModal;
