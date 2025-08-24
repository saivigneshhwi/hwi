import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  MapPin, 
  Users, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  X,
  Edit,
  Navigation
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import TicketModal from '../components/TicketModal';

const Tickets = () => {
  const [tickets, setTickets] = useState([]);
  const [filteredTickets, setFilteredTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    priority: '',
    region: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchTickets();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [tickets, filters, searchTerm]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/sos/');
      setTickets(response.data);
    } catch (error) {
      toast.error('Failed to fetch tickets');
      console.error('Tickets fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...tickets];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(ticket =>
        ticket.place.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    if (filters.status) {
      filtered = filtered.filter(ticket => ticket.status === filters.status);
    }

    // Apply category filter
    if (filters.category) {
      filtered = filtered.filter(ticket => ticket.category === filters.category);
    }

    // Apply priority filter
    if (filters.priority) {
      filtered = filtered.filter(ticket => ticket.priority === parseInt(filters.priority));
    }

    // Apply region filter
    if (filters.region) {
      filtered = filtered.filter(ticket => {
        const lon = ticket.longitude;
        if (filters.region === 'western') return lon >= 72.0 && lon <= 75.0;
        if (filters.region === 'central') return lon >= 75.0 && lon <= 78.0;
        if (filters.region === 'vidarbha') return lon >= 78.0 && lon <= 81.0;
        return true;
      });
    }

    setFilteredTickets(filtered);
  };

  const handleTicketClick = (ticket) => {
    setSelectedTicket(ticket);
    setShowModal(true);
  };

  const handleStatusUpdate = async (ticketId, newStatus, notes) => {
    try {
      await axios.put(`/api/sos/${ticketId}`, {
        status: newStatus,
        notes: notes
      });
      
      // Update local state
      setTickets(tickets.map(ticket => 
        ticket.id === ticketId 
          ? { ...ticket, status: newStatus, notes: notes }
          : ticket
      ));
      
      toast.success('Ticket status updated successfully');
      setShowModal(false);
    } catch (error) {
      toast.error('Failed to update ticket status');
      console.error('Status update error:', error);
    }
  };

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

  const getStatusColor = (status) => {
    const colors = {
      'Pending': 'bg-yellow-100 text-yellow-800',
      'In Progress': 'bg-blue-100 text-blue-800',
      'Done': 'bg-green-100 text-green-800',
      'Cancelled': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors['Pending'];
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Pending': return <Clock className="w-4 h-4" />;
      case 'In Progress': return <AlertTriangle className="w-4 h-4" />;
      case 'Done': return <CheckCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="spinner"></div>
      </div>
    );
  }

  const categories = [...new Set(tickets.map(ticket => ticket.category))];
  const regions = [
    { value: 'western', label: 'Western Maharashtra' },
    { value: 'central', label: 'Central Maharashtra' },
    { value: 'vidarbha', label: 'Vidarbha' }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">SOS Tickets</h1>
          <p className="text-gray-600">Manage emergency response requests</p>
        </div>
        <div className="text-sm text-gray-500">
          Total: {tickets.length} • Pending: {tickets.filter(t => t.status === 'Pending').length}
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Done">Done</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          {/* Priority Filter */}
          <div>
            <select
              value={filters.priority}
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Priorities</option>
              <option value="1">Priority 1</option>
              <option value="2">Priority 2</option>
              <option value="3">Priority 3</option>
              <option value="4">Priority 4</option>
              <option value="5">Priority 5</option>
            </select>
          </div>

          {/* Region Filter */}
          <div>
            <select
              value={filters.region}
              onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Regions</option>
              {regions.map(region => (
                <option key={region.value} value={region.value}>{region.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Tickets List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Tickets ({filteredTickets.length})
          </h3>
        </div>
        <div className="divide-y divide-gray-200">
          {filteredTickets.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No tickets found matching the current filters.
            </div>
          ) : (
            filteredTickets.map((ticket) => (
              <div
                key={ticket.id}
                onClick={() => handleTicketClick(ticket)}
                className="p-6 hover:bg-gray-50 cursor-pointer transition-colors duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                        Priority {ticket.priority}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)} flex items-center space-x-1`}>
                        {getStatusIcon(ticket.status)}
                        <span>{ticket.status}</span>
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      {ticket.category} - {ticket.place}
                    </h4>
                    
                    <p className="text-gray-600 mb-3 line-clamp-2">
                      {ticket.text}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Users className="w-4 h-4" />
                        <span>{ticket.people} people affected</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-4 h-4" />
                        <span>{ticket.latitude.toFixed(4)}, {ticket.longitude.toFixed(4)}</span>
                      </div>
                      {ticket.assigned_to && (
                        <div className="flex items-center space-x-1">
                          <span>Assigned to: {ticket.assigned_to}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="ml-4 flex items-center space-x-2">
                    <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                      <Navigation className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Ticket Modal */}
      {showModal && selectedTicket && (
        <TicketModal
          ticket={selectedTicket}
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          onStatusUpdate={handleStatusUpdate}
        />
      )}
    </div>
  );
};

export default Tickets;
