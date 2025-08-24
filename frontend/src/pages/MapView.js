import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Filter, 
  Search,
  MapPin,
  Home,
  Activity,
  AlertTriangle,
  X
} from 'lucide-react';
import MapView from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import axios from 'axios';
import toast from 'react-hot-toast';

const MapViewPage = () => {
  const [viewState, setViewState] = useState({
    longitude: 75.0, // Central Maharashtra
    latitude: 19.0,
    zoom: 7
  });
  const [sosData, setSosData] = useState([]);
  const [shelters, setShelters] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [layers, setLayers] = useState({
    sos: true,
    shelters: true,
    hospitals: true
  });
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    priority: ''
  });
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example';

  useEffect(() => {
    fetchMapData();
  }, []);

  const fetchMapData = async () => {
    try {
      setLoading(true);
      const [sosRes, sheltersRes, hospitalsRes] = await Promise.all([
        axios.get('/api/sos/map'),
        axios.get('/api/shelters/'),
        axios.get('/api/hospitals/')
      ]);

      setSosData(sosRes.data);
      setShelters(sheltersRes.data);
      setHospitals(hospitalsRes.data);
    } catch (error) {
      toast.error('Failed to fetch map data');
      console.error('Map data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      1: '#6b7280',
      2: '#3b82f6',
      3: '#f59e0b',
      4: '#f97316',
      5: '#ef4444'
    };
    return colors[priority] || colors[1];
  };

  const getStatusColor = (status) => {
    const colors = {
      'Pending': '#f59e0b',
      'In Progress': '#3b82f6',
      'Done': '#22c55e',
      'Cancelled': '#6b7280'
    };
    return colors[status] || colors['Pending'];
  };

  const handleMarkerClick = (marker) => {
    setSelectedMarker(marker);
  };

  const closePopup = () => {
    setSelectedMarker(null);
  };

  const filteredSosData = sosData.filter(sos => {
    if (filters.status && sos.status !== filters.status) return false;
    if (filters.category && sos.category !== filters.category) return false;
    if (filters.priority && sos.priority !== parseInt(filters.priority)) return false;
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return sos.place.toLowerCase().includes(search) || 
             sos.category.toLowerCase().includes(search);
    }
    return true;
  });

  const categories = [...new Set(sosData.map(sos => sos.category))];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="h-full relative">
      {/* Map Controls */}
      <div className="absolute top-4 left-4 z-10 space-y-3">
        {/* Search */}
        <div className="bg-white rounded-lg shadow-lg p-3 w-80">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search locations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Layer Controls */}
        <div className="bg-white rounded-lg shadow-lg p-3">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
            <Layers className="w-4 h-4" />
            <span>Layers</span>
          </h3>
          <div className="space-y-2">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={layers.sos}
                onChange={(e) => setLayers({ ...layers, sos: e.target.checked })}
                className="rounded text-blue-600"
              />
              <span className="text-sm">SOS Requests</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={layers.shelters}
                onChange={(e) => setLayers({ ...layers, shelters: e.target.checked })}
                className="rounded text-blue-600"
              />
              <span className="text-sm">Shelters</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={layers.hospitals}
                onChange={(e) => setLayers({ ...layers, hospitals: e.target.checked })}
                className="rounded text-blue-600"
              />
              <span className="text-sm">Hospitals</span>
            </label>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-3">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </h3>
          <div className="space-y-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Done">Done</option>
            </select>
            
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
            
            <select
              value={filters.priority}
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              <option value="1">Priority 1</option>
              <option value="2">Priority 2</option>
              <option value="3">Priority 3</option>
              <option value="4">Priority 4</option>
              <option value="5">Priority 5</option>
            </select>
          </div>
        </div>
      </div>

      {/* Map */}
      <MapView
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/streets-v11"
      >
        {/* SOS Markers */}
        {layers.sos && filteredSosData.map((sos) => (
          <div
            key={sos.id}
            style={{
              position: 'absolute',
              left: `${((sos.longitude + 180) / 360) * 100}%`,
              top: `${((90 - sos.latitude) / 180) * 100}%`,
              transform: 'translate(-50%, -50%)',
              cursor: 'pointer'
            }}
            onClick={() => handleMarkerClick({ type: 'sos', data: sos })}
          >
            <div
              className="w-6 h-6 rounded-full border-2 border-white shadow-lg animate-pulse"
              style={{ backgroundColor: getPriorityColor(sos.priority) }}
            ></div>
          </div>
        ))}

        {/* Shelter Markers */}
        {layers.shelters && shelters.map((shelter) => (
          <div
            key={shelter.id}
            style={{
              position: 'absolute',
              left: `${((shelter.longitude + 180) / 360) * 100}%`,
              top: `${((90 - shelter.latitude) / 180) * 100}%`,
              transform: 'translate(-50%, -50%)',
              cursor: 'pointer'
            }}
            onClick={() => handleMarkerClick({ type: 'shelter', data: shelter })}
          >
            <div className="w-5 h-5 bg-green-500 rounded-full border-2 border-white shadow-lg"></div>
          </div>
        ))}

        {/* Hospital Markers */}
        {layers.hospitals && hospitals.map((hospital) => (
          <div
            key={hospital.id}
            style={{
              position: 'absolute',
              left: `${((hospital.longitude + 180) / 360) * 100}%`,
              top: `${((90 - hospital.latitude) / 180) * 100}%`,
              transform: 'translate(-50%, -50%)',
              cursor: 'pointer'
            }}
            onClick={() => handleMarkerClick({ type: 'hospital', data: hospital })}
          >
            <div className="w-5 h-5 bg-blue-500 rounded-full border-2 border-white shadow-lg"></div>
          </div>
        ))}
      </MapView>

      {/* Marker Popup */}
      {selectedMarker && (
        <div className="absolute top-4 right-4 z-10 bg-white rounded-lg shadow-lg p-4 max-w-sm">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              {selectedMarker.type === 'sos' && <AlertTriangle className="w-5 h-5 text-red-500" />}
              {selectedMarker.type === 'shelter' && <Home className="w-5 h-5 text-green-500" />}
              {selectedMarker.type === 'hospital' && <Activity className="w-5 h-5 text-blue-500" />}
              <h3 className="font-semibold text-gray-900">
                {selectedMarker.type === 'sos' ? 'SOS Request' : 
                 selectedMarker.type === 'shelter' ? 'Shelter' : 'Hospital'}
              </h3>
            </div>
            <button
              onClick={closePopup}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {selectedMarker.type === 'sos' && (
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Category:</span> {selectedMarker.data.category}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Location:</span> {selectedMarker.data.place}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">People:</span> {selectedMarker.data.people}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Priority:</span> {selectedMarker.data.priority}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Status:</span> {selectedMarker.data.status}
              </p>
            </div>
          )}

          {selectedMarker.type === 'shelter' && (
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Name:</span> {selectedMarker.data.name}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Address:</span> {selectedMarker.data.address}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Capacity:</span> {selectedMarker.data.capacity}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Occupancy:</span> {selectedMarker.data.current_occupancy}
              </p>
            </div>
          )}

          {selectedMarker.type === 'hospital' && (
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Name:</span> {selectedMarker.data.name}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Address:</span> {selectedMarker.data.address}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Total Beds:</span> {selectedMarker.data.total_beds}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Available:</span> {selectedMarker.data.available_beds}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">Legend</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <span>High Priority SOS</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span>Shelters</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
            <span>Hospitals</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapViewPage;
