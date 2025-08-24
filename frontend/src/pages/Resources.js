import React, { useState, useEffect } from 'react';
import { 
  Home, 
  Activity, 
  Users, 
  MapPin, 
  Phone, 
  Search,
  Filter,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  X,
  Anchor,
  Shield
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { availabilityData } from '../data/availability';

const Resources = () => {
  const [shelters, setShelters] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('shelters');
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    region: ''
  });

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const [sheltersRes, hospitalsRes] = await Promise.all([
        axios.get('/api/shelters/'),
        axios.get('/api/hospitals/')
      ]);

      setShelters(sheltersRes.data);
      setHospitals(hospitalsRes.data);
    } catch (error) {
      toast.error('Failed to fetch resources');
      console.error('Resources fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShelterUpdate = async (shelterId, updates) => {
    try {
      await axios.put(`/api/shelters/${shelterId}`, updates);
      setShelters(shelters.map(shelter => 
        shelter.id === shelterId ? { ...shelter, ...updates } : shelter
      ));
      toast.success('Shelter updated successfully');
    } catch (error) {
      toast.error('Failed to update shelter');
    }
  };

  const handleHospitalUpdate = async (hospitalId, updates) => {
    try {
      await axios.put(`/api/hospitals/${hospitalId}`, updates);
      setHospitals(hospitals.map(hospital => 
        hospital.id === hospitalId ? { ...hospital, ...updates } : hospital
      ));
      toast.success('Hospital updated successfully');
    } catch (error) {
      toast.error('Failed to update hospital');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Available': 'bg-green-100 text-green-800',
      'Active': 'bg-blue-100 text-blue-800',
      'Full': 'bg-red-100 text-red-800',
      'Inactive': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors['Available'];
  };

  const getRegionName = (longitude) => {
    if (longitude >= 72.0 && longitude <= 75.0) return 'Western Maharashtra';
    if (longitude >= 75.0 && longitude <= 78.0) return 'Central Maharashtra';
    if (longitude >= 78.0 && longitude <= 81.0) return 'Vidarbha';
    return 'Unknown';
  };

  const filteredShelters = shelters.filter(shelter => {
    if (searchTerm && !shelter.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (filters.type && shelter.type !== filters.type) return false;
    if (filters.status && shelter.status !== filters.status) return false;
    if (filters.region) {
      const region = getRegionName(shelter.longitude);
      if (region.toLowerCase() !== filters.region.toLowerCase()) return false;
    }
    return true;
  });

  const filteredHospitals = hospitals.filter(hospital => {
    if (searchTerm && !hospital.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (filters.region) {
      const region = getRegionName(hospital.longitude);
      if (region.toLowerCase() !== filters.region.toLowerCase()) return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="spinner"></div>
      </div>
    );
  }

  const shelterTypes = [...new Set(shelters.map(s => s.type))];
  const shelterStatuses = [...new Set(shelters.map(s => s.status))];
  const regions = ['Western Maharashtra', 'Central Maharashtra', 'Vidarbha'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Resources</h1>
          <p className="text-gray-600">Manage shelters, hospitals, and resource centers</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Shelters: {shelters.length} • Hospitals: {hospitals.length}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('shelters')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'shelters'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Shelters ({shelters.length})
          </button>
          <button
            onClick={() => setActiveTab('hospitals')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'hospitals'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Hospitals ({hospitals.length})
          </button>
          <button
            onClick={() => setActiveTab('availability')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'availability'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Availability
          </button>
        </nav>
      </div>

      {/* Filters and Search */}
      {activeTab !== 'availability' && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search resources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Type Filter (Shelters only) */}
            {activeTab === 'shelters' && (
              <div>
                <select
                  value={filters.type}
                  onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  {shelterTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Status Filter (Shelters only) */}
            {activeTab === 'shelters' && (
              <div>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Status</option>
                  {shelterStatuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Region Filter */}
            <div>
              <select
                value={filters.region}
                onChange={(e) => setFilters({ ...filters, region: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Regions</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Resources Content */}
      {activeTab === 'shelters' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Shelters ({filteredShelters.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredShelters.map((shelter) => (
              <ShelterCard
                key={shelter.id}
                shelter={shelter}
                onUpdate={handleShelterUpdate}
                region={getRegionName(shelter.longitude)}
              />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'hospitals' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Hospitals ({filteredHospitals.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredHospitals.map((hospital) => (
              <HospitalCard
                key={hospital.id}
                hospital={hospital}
                onUpdate={handleHospitalUpdate}
                region={getRegionName(hospital.longitude)}
              />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'availability' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Resource Availability
            </h3>
            <p className="text-sm text-gray-600 mt-1">Current status of emergency response equipment</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Boats */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                    <Anchor className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold text-blue-900">Boats</h4>
                    <p className="text-blue-600">Emergency Response Vessels</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-blue-700 font-medium">Available:</span>
                    <span className="text-2xl font-bold text-blue-900">{availabilityData.boats.left}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-700 font-medium">Total:</span>
                    <span className="text-lg text-blue-800">{availabilityData.boats.total}</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(availabilityData.boats.left / availabilityData.boats.total) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-center">
                    <span className="text-sm text-blue-600">
                      {Math.round((availabilityData.boats.left / availabilityData.boats.total) * 100)}% Available
                    </span>
                  </div>
                </div>
              </div>

              {/* Life Jackets */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold text-green-900">Life Jackets</h4>
                    <p className="text-green-600">Safety Equipment</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-green-700 font-medium">Available:</span>
                    <span className="text-2xl font-bold text-green-900">{availabilityData.lifeJackets.left}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-green-700 font-medium">Total:</span>
                    <span className="text-lg text-green-800">{availabilityData.lifeJackets.total}</span>
                  </div>
                  <div className="w-full bg-green-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(availabilityData.lifeJackets.left / availabilityData.lifeJackets.total) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-center">
                    <span className="text-sm text-green-600">
                      {Math.round((availabilityData.lifeJackets.left / availabilityData.lifeJackets.total) * 100)}% Available
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Summary Stats */}
            <div className="mt-8 p-6 bg-gray-50 rounded-xl">
              <h5 className="text-lg font-semibold text-gray-900 mb-4">Summary</h5>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{availabilityData.boats.left}</div>
                  <div className="text-sm text-gray-600">Boats Available</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{availabilityData.lifeJackets.left}</div>
                  <div className="text-sm text-gray-600">Life Jackets Available</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {availabilityData.boats.left + availabilityData.lifeJackets.left}
                  </div>
                  <div className="text-sm text-gray-600">Total Items Available</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Shelter Card Component
const ShelterCard = ({ shelter, onUpdate, region }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    current_occupancy: shelter.current_occupancy,
    status: shelter.status
  });

  const getStatusColor = (status) => {
    const colors = {
      'Available': 'bg-green-100 text-green-800',
      'Active': 'bg-blue-100 text-blue-800',
      'Full': 'bg-red-100 text-red-800',
      'Inactive': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors['Available'];
  };

  const handleSave = () => {
    onUpdate(shelter.id, editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      current_occupancy: shelter.current_occupancy,
      status: shelter.status
    });
    setIsEditing(false);
  };

  return (
    <div className="p-6 hover:bg-gray-50 transition-colors duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Home className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900">{shelter.name}</h4>
              <p className="text-sm text-gray-500">{region}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">{shelter.address}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {shelter.current_occupancy}/{shelter.capacity} occupied
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Phone className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">{shelter.contact_phone}</span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(shelter.status)}`}>
              {shelter.status}
            </span>
            <span className="text-sm text-gray-500">Type: {shelter.type}</span>
            <span className="text-sm text-gray-500">Contact: {shelter.contact_person}</span>
          </div>
        </div>

        <div className="ml-4 flex items-center space-x-2">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="p-2 text-green-600 hover:text-green-700 rounded-lg hover:bg-green-100"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
              <button
                onClick={handleCancel}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="w-4 h-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <Edit className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Edit Form */}
      {isEditing && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Occupancy
              </label>
              <input
                type="number"
                min="0"
                max={shelter.capacity}
                value={editData.current_occupancy}
                onChange={(e) => setEditData({ ...editData, current_occupancy: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={editData.status}
                onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="Available">Available</option>
                <option value="Active">Active</option>
                <option value="Full">Full</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Hospital Card Component
const HospitalCard = ({ hospital, onUpdate, region }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    available_beds: hospital.available_beds,
    available_icu: hospital.available_icu
  });

  const handleSave = () => {
    onUpdate(hospital.id, editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      available_beds: hospital.available_beds,
      available_icu: hospital.available_icu
    });
    setIsEditing(false);
  };

  return (
    <div className="p-6 hover:bg-gray-50 transition-colors duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900">{hospital.name}</h4>
              <p className="text-sm text-gray-500">{region}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">{hospital.address}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {hospital.available_beds}/{hospital.total_beds} beds available
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Phone className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">{hospital.contact_phone}</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              ICU Beds: {hospital.available_icu}/{hospital.icu_beds} available
            </span>
            <span className="text-sm text-gray-500">
              Utilization: {Math.round(((hospital.total_beds - hospital.available_beds) / hospital.total_beds) * 100)}%
            </span>
          </div>
        </div>

        <div className="ml-4 flex items-center space-x-2">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="p-2 text-green-600 hover:text-green-700 rounded-lg hover:bg-green-100"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
              <button
                onClick={handleCancel}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="w-4 h-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <Edit className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Edit Form */}
      {isEditing && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Available Beds
              </label>
              <input
                type="number"
                min="0"
                max={hospital.total_beds}
                value={editData.available_beds}
                onChange={(e) => setEditData({ ...editData, available_beds: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Available ICU Beds
              </label>
              <input
                type="number"
                min="0"
                max={hospital.icu_beds}
                value={editData.available_icu}
                onChange={(e) => setEditData({ ...editData, available_icu: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Resources;
