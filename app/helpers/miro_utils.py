import requests
import json
import re
import os
import streamlit as st
import math

def extract_structure_from_summary(summary_text):
    """Extract the hierarchical structure from a summary text."""
    lines = summary_text.split('\n')
    
    structure = {
        "central_topic": None,
        "main_topics": []
    }
    
    current_main_topic = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Central topic (main title)
        if line.startswith('# '):
            structure["central_topic"] = line[2:].strip()
        
        # Main topics (second level headings)
        elif line.startswith('## '):
            current_main_topic = {
                "title": line[3:].strip(),
                "subtopics": []
            }
            structure["main_topics"].append(current_main_topic)
        
        # Subtopics (bullet points)
        elif line.startswith('- ') and current_main_topic:
            current_main_topic["subtopics"].append(line[2:].strip())
    
    # If no central topic was found, use a default
    if not structure["central_topic"] and structure["main_topics"]:
        structure["central_topic"] = "Book Summary"
    
    return structure

def create_miro_mindmap(summary_text, miro_access_token, board_id=None):
    """Create a mind map in Miro from a summary text."""
    if not miro_access_token:
        return {"success": False, "error": "Miro access token is required"}
    
    # Extract the structure from the summary
    structure = extract_structure_from_summary(summary_text)
    
    if not structure["central_topic"]:
        return {"success": False, "error": "Could not extract central topic from summary"}
    
    try:
        # Create a new board if board_id isn't provided
        if not board_id:
            board = create_miro_board(miro_access_token, structure["central_topic"])
            if not board or not board.get("id"):
                return {"success": False, "error": "Failed to create Miro board"}
            board_id = board["id"]
        
        # IMPORTANT: Do NOT remove the trailing = character from board ID
        
        # Check if the board exists before trying to add items
        if not verify_board_access(miro_access_token, board_id):
            return {"success": False, "error": f"Could not access board with ID {board_id}"}
        
        # Create the mind map structure
        success, error_msg = create_mindmap_structure(miro_access_token, board_id, structure)
        if not success:
            return {"success": False, "error": error_msg or "Failed to create mind map structure"}
        
        # Get a shareable link to the board
        board_link = f"https://miro.com/app/board/{board_id}/"
        
        return {
            "success": True,
            "board_id": board_id,
            "board_url": board_link,
            "structure": structure
        }
    except Exception as e:
        st.error(f"Error in Miro mind map creation: {str(e)}")
        return {"success": False, "error": str(e)}

def verify_board_access(access_token, board_id):
    """Verify that the board exists and is accessible."""
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            f"https://api.miro.com/v2/boards/{board_id}",
            headers=headers
        )
        
        return response.status_code == 200
    except:
        return False

def create_miro_board(access_token, board_name):
    """Create a new Miro board."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Limit board name length to 60 characters (Miro API requirement)
    prefix = "Mind Map: "
    max_name_length = 60 - len(prefix)  # Reserve space for the prefix
    
    if board_name and len(board_name) > max_name_length:
        board_name = board_name[:max_name_length-3] + "..."
    
    data = {
        "name": f"{prefix}{board_name}",
        "description": f"Mind map automatically generated from book summary"
    }
    
    try:
        response = requests.post(
            "https://api.miro.com/v2/boards",
            headers=headers,
            json=data  # Using json=data format for Miro API
        )
        
        # Log detailed response for debugging
        if response.status_code != 201 and response.status_code != 200:
            st.error(f"Error creating board: {response.status_code} - {response.text}")
            return None
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating Miro board: {str(e)}")
        return None

def create_mind_map_shape(access_token, board_id, text, x=0, y=0, width=200, height=100, style=None):
    """Create a mind map shape on a Miro board.
    Now uses cards instead of sticky notes."""
    
    # Use cards instead of sticky notes
    return create_miro_card(access_token, board_id, text, x, y, width, height, style)

def create_mindmap_structure(access_token, board_id, structure):
    """Create the mind map structure on a Miro board."""
    try:
        # Create the central topic
        central_node = create_mind_map_shape(
            access_token, 
            board_id, 
            structure["central_topic"],
            x=0, 
            y=0,
            width=300,  # Larger central topic 
            height=120,
            style={
                "fillColor": "light_blue"
            }
        )
        
        if not central_node or not central_node.get("id"):
            return False, "Failed to create central topic"
            
        # Calculate positions for main topics
        num_main_topics = len(structure["main_topics"])
        if num_main_topics == 0:
            return True, None  # No main topics to create
            
        # Larger radius for main topics (full 360° layout)
        radius = 900  
        
        for i, main_topic in enumerate(structure["main_topics"]):
            # Calculate position in a full 360-degree circle
            angle = (i / num_main_topics) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # Make title safe for API
            title = main_topic["title"]
            if len(title) > 255:  # Miro API limit for sticky note content
                title = title[:252] + "..."
            
            # Create the main topic node
            main_node = create_mind_map_shape(
                access_token,
                board_id,
                title,
                x=x,
                y=y,
                width=250,
                height=100,
                style={
                    "fillColor": "light_pink" if i % 2 == 0 else "light_green"
                }
            )
            
            if not main_node or not main_node.get("id"):
                continue
                
            # Create connector between central topic and main topic
            create_connector(
                access_token,
                board_id,
                central_node["id"],
                main_node["id"],
                {"stroke": "#455666", "strokeWidth": "2"}
            )
            
            # Create subtopics
            subtopic_radius = 400  # Large distance from main topic
            num_subtopics = len(main_topic["subtopics"])
            
            for j, subtopic in enumerate(main_topic["subtopics"]):
                # Calculate direction vector from central node to main topic
                dir_x = x
                dir_y = y
                dir_length = math.sqrt(dir_x**2 + dir_y**2)
                dir_x = dir_x / dir_length if dir_length > 0 else 0
                dir_y = dir_y / dir_length if dir_length > 0 else 0
                
                # Calculate angle for spreading subtopics while keeping them on the same side
                # as their parent main topic is to the central node
                spread_range = math.pi / 2  # 90 degree spread
                
                # Position subtopics in a fan pattern on the same side as the main topic
                sub_angle_offset = (j - (num_subtopics - 1) / 2) * (spread_range / max(num_subtopics - 1, 1))
                
                # Calculate the main angle from central to main topic
                main_angle = math.atan2(y, x)
                
                # Apply the offset to the main angle
                subtopic_angle = main_angle + sub_angle_offset
                
                # Calculate position based on this angle
                sub_x = x + subtopic_radius * math.cos(subtopic_angle)
                sub_y = y + subtopic_radius * math.sin(subtopic_angle)
                
                # Make subtopic text safe for API
                if len(subtopic) > 255:  # Miro API limit
                    subtopic = subtopic[:252] + "..."
                
                # Create the subtopic node
                sub_node = create_mind_map_shape(
                    access_token,
                    board_id,
                    subtopic,
                    x=sub_x,
                    y=sub_y,
                    width=200,
                    height=80,
                    style={
                        "fillColor": "light_yellow"
                    }
                )
                
                if not sub_node or not sub_node.get("id"):
                    continue
                    
                # Create connector between main topic and subtopic
                create_connector(
                    access_token,
                    board_id,
                    main_node["id"],
                    sub_node["id"],
                    {"stroke": "#455666", "strokeWidth": "1"}
                )
        
        return True, None
    except Exception as e:
        st.error(f"Error creating mind map structure: {str(e)}")
        return False, str(e)

def create_miro_card(access_token, board_id, title, x=0, y=0, width=200, height=100, style=None):
    """Create a card on a Miro board."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Make sure title is not None
    if title is None:
        title = "Untitled"
    
    # Ensure title is a string and limit length
    title = str(title)
    if len(title) > 255:  # Miro API limit
        title = title[:252] + "..."
    
    # Card data structure for Miro API - removed unsupported fillColor
    payload = {
        "data": {
            "title": title
        }
    }
    
    # Only add position if coordinates are provided
    if x != 0 or y != 0:
        payload["position"] = {
            "x": x,
            "y": y
        }
    
    try:
        response = requests.post(
            f"https://api.miro.com/v2/boards/{board_id}/cards",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201 and response.status_code != 200:
            st.error(f"Error creating card: {response.status_code} - {response.text}")
            # Fall back to sticky note if card creation fails
            return create_miro_sticky_note(access_token, board_id, title, x, y, width, height, style)
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating Miro card: {str(e)}")
        # Fall back to sticky note if card creation fails
        return create_miro_sticky_note(access_token, board_id, title, x, y, width, height, style)

def create_miro_sticky_note(access_token, board_id, content, x=0, y=0, width=200, height=100, style=None):
    """Create a sticky note on a Miro board as a fallback."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Make sure content is not None
    if content is None:
        content = "Untitled"
    
    # Ensure content is a string and limit length
    content = str(content)
    if len(content) > 255:  # Miro API limit
        content = content[:252] + "..."
    
    # Default color based on Miro's supported sticky note colors
    default_color = "light_yellow"
    
    # Convert style to Miro's supported colors
    note_color = default_color
    if style and "fillColor" in style:
        note_color = style["fillColor"]
    
    # Ultra minimal data structure that should work with current Miro API
    payload = {
        "data": {
            "content": content
        },
        "style": {
            "fillColor": note_color
        }
    }
    
    # Only add position if coordinates are provided
    if x != 0 or y != 0:
        payload["position"] = {
            "x": x,
            "y": y
        }
    
    try:
        response = requests.post(
            f"https://api.miro.com/v2/boards/{board_id}/sticky_notes",
            headers=headers,
            json=payload  # Using json=payload format for Miro API
        )
        
        if response.status_code != 201 and response.status_code != 200:
            st.error(f"Error creating sticky note: {response.status_code} - {response.text}")
            return None
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating Miro sticky note: {str(e)}")
        return None

def create_connector(access_token, board_id, start_item_id, end_item_id, style=None):
    """Create a connector between two items on a Miro board."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Simplified minimal data structure for connectors
    payload = {
        "startItem": {
            "id": start_item_id
        },
        "endItem": {
            "id": end_item_id
        }
    }
    
    try:
        response = requests.post(
            f"https://api.miro.com/v2/boards/{board_id}/connectors",
            headers=headers,
            json=payload  # Using json=payload format for Miro API
        )
        
        if response.status_code != 201 and response.status_code != 200:
            st.error(f"Error creating connector: {response.status_code} - {response.text}")
            return None
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating connector: {str(e)}")
        return None 