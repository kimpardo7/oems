# Bentley Dealers Data Summary

## Overview
Successfully extracted dealer information from Bentley Motors dealer locator HTML data.

## Statistics
- **Total Dealers**: 62
- **Brand**: Bentley
- **Source**: Bentley Motors dealer locator
- **Extraction Date**: 2024-01-27

## Data Structure
Each dealer entry contains:
- **Name**: Dealer name (e.g., "Bentley Atlanta")
- **Departments**: Services offered (New Car Sales, Pre-Owned Sales, Service)
- **Address**: Street, city, and state/zip information
- **Phone**: Contact phone number
- **Website**: Dealer website URL
- **Coordinates**: Latitude and longitude for mapping
- **Opening Hours**: Business hours for each day of the week

## Geographic Distribution
The 62 Bentley dealers are distributed across major metropolitan areas in the United States, including:

- **California**: Multiple locations (Beverly Hills, Los Angeles, San Francisco, San Diego, etc.)
- **Texas**: Austin, Dallas, Houston, San Antonio
- **Florida**: Miami, Fort Lauderdale, Naples, Orlando, Palm Beach
- **New York**: Manhattan, Long Island, Greenwich
- **Illinois**: Chicago area (Downers Grove, Northbrook)
- **And many other states**

## Data Quality
- All dealers have complete contact information
- Geographic coordinates available for mapping applications
- Opening hours provided for most locations
- Department information clearly categorized

## File Location
- **JSON Data**: `data/bentley.json`
- **Extraction Script**: `scripts/extract_bentley_dealers.py`
- **Source HTML**: `bentily.txt`

## Usage
The JSON file can be used for:
- Dealer locator applications
- Geographic mapping
- Contact management systems
- Business intelligence analysis
