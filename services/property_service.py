"""
Property Service - Building and Property Management
==============================================

Handles:
- Building CRUD operations  
- Property CRUD operations
- Building-Property relationships
- API endpoints for AJAX
"""

from sqlmodel import select, func
from typing import List, Dict, Any, Optional
from models import Building, Property
from .base import BaseService


class PropertyService(BaseService):
    """Property and Building management service with user context support"""
    
    # ===================
    # BUILDING OPERATIONS  
    # ===================
    
    def get_buildings_with_counts(self) -> List[Dict[str, Any]]:
        """Get all buildings with property counts for display"""
        buildings = self.session.exec(select(Building)).all()
        
        building_data = []
        for b in buildings:
            num_props = self.session.exec(
                select(func.count()).where(Property.building_id == b.id)
            ).one()
            building_data.append({
                "id": b.id,
                "building_name": b.building_name,
                "building_code": b.building_code,
                "address": b.address,
                "num_properties": num_props
            })
        
        self.log_activity("get_buildings_with_counts", {"count": len(building_data)})
        return building_data
    
    def create_building(self, building_name: str, building_code: Optional[str] = None, 
                       address: Optional[str] = None) -> Dict[str, Any]:
        """Create new building with validation"""
        try:
            # Check permissions if user context available
            if self.current_user:
                if not self.check_permission("building_create"):
                    return self.error_response("Insufficient permissions to create building", 403)
            
            new_building = Building(
                building_name=building_name,
                building_code=building_code,
                address=address
            )
            self.session.add(new_building)
            self.session.commit()
            
            self.log_activity("create_building", {
                "building_id": new_building.id,
                "building_name": building_name
            })
            
            return self.success_response("Building created successfully", {
                "building_id": new_building.id
            })
            
        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to create building: {str(e)}", 500)
    
    # ====================
    # PROPERTY OPERATIONS
    # ====================
    
    def get_properties_with_buildings(self) -> List[Dict[str, Any]]:
        """Get all properties joined with building information"""
        query = (
            select(Property, Building.building_name)
            .join(Building, Property.building_id == Building.id, isouter=True)
            .order_by(Property.property_name)
        )
        results = self.session.exec(query).all()
        
        properties = []
        for prop, building_name in results:
            properties.append({
                "id": prop.id,
                "property_name": prop.property_name,
                "property_short": prop.property_short,
                "building_name": building_name or "N/A",
                "unit_number": prop.unit_number,
                "airbnb_name": prop.airbnb_name,
            })
        
        self.log_activity("get_properties_with_buildings", {"count": len(properties)})
        return properties
    
    def create_property(self, property_name: str, building_id: int, 
                       property_short: Optional[str] = None, 
                       unit_number: Optional[str] = None,
                       airbnb_name: Optional[str] = None) -> Dict[str, Any]:
        """Create new property with building validation"""
        try:
            # Check permissions if user context available
            if self.current_user:
                if not self.check_permission("property_create"):
                    return self.error_response("Insufficient permissions to create property", 403)
            
            # Validate building exists
            building = self.session.get(Building, building_id)
            if not building:
                return self.error_response("Building not found", 404)
            
            new_property = Property(
                property_name=property_name,
                property_short=property_short,
                building_id=building_id,
                unit_number=unit_number,
                airbnb_name=airbnb_name
            )
            self.session.add(new_property)
            self.session.commit()
            
            self.log_activity("create_property", {
                "property_id": new_property.id,
                "property_name": property_name,
                "building_id": building_id
            })
            
            return self.success_response("Property created successfully", {
                "property_id": new_property.id
            })
            
        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to create property: {str(e)}", 500)
    
    # ==============
    # API ENDPOINTS
    # ==============
    
    def get_buildings_api(self) -> List[Dict[str, Any]]:
        """Simple building list for API/AJAX usage"""
        buildings = self.session.exec(select(Building)).all()
        return [{"id": b.id, "name": b.building_name} for b in buildings]
    
    def get_properties_api(self) -> List[Dict[str, Any]]:
        """Simple property list for API/AJAX usage"""  
        properties = self.session.exec(select(Property)).all()
        return [{"id": p.id, "name": p.property_name, "building_id": p.building_id} 
                for p in properties]
    
    # =================
    # BUSINESS QUERIES
    # =================
    
    def get_properties_by_building(self, building_id: int) -> List[Property]:
        """Get all properties in specific building"""
        return self.session.exec(
            select(Property).where(Property.building_id == building_id)
        ).all()
    
    def search_properties(self, search_term: str) -> List[Dict[str, Any]]:
        """Search properties by name or building"""
        query = (
            select(Property, Building.building_name)
            .join(Building, Property.building_id == Building.id, isouter=True)
            .where(
                Property.property_name.contains(search_term) |
                Property.airbnb_name.contains(search_term) |
                Building.building_name.contains(search_term)
            )
        )
        results = self.session.exec(query).all()
        
        properties = []
        for prop, building_name in results:
            properties.append({
                "id": prop.id,
                "property_name": prop.property_name,
                "property_short": prop.property_short,
                "building_name": building_name or "N/A",
                "unit_number": prop.unit_number,
                "airbnb_name": prop.airbnb_name,
            })
        
        return properties