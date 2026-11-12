# =============================================================================
# CivicSense AI — Verified Seed Civic Corpus
# =============================================================================
# Verified jurisdiction and civic-service records for RAG semantic search.
# =============================================================================

from app.rag.ingestion import CivicDocument, DocumentSource, VerificationStatus


SEED_CIVIC_DOCUMENTS: list[CivicDocument] = [
    CivicDocument(
        id="MCG-GURUGRAM-CIVIC-GRIEVANCE-01",
        category="general_civic_services",
        source=DocumentSource(
            authority_name="Municipal Corporation of Gurugram",
            title="Official civic grievance and contact information",
            reference_id="https://www.mcg.gov.in/",
            url="https://www.mcg.gov.in/",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Corporation of Gurugram",
            verified_at="2026-10-22",
        ),
        text=(
            "The official Municipal Corporation of Gurugram website provides a "
            "Report Civic Issue and Track Status service. It lists the MCG "
            "toll-free number 18001801817 and the head office at Sector 34, "
            "Gurugram, Haryana 122001. This source supports a general MCG civic "
            "grievance route. Official field inspection protocols apply to all reported issues."
        ),
    ),
    CivicDocument(
        id="IRC-SP20-ROAD-MAINTENANCE-01",
        category="pothole_and_road_damage",
        source=DocumentSource(
            authority_name="Indian Roads Congress (IRC)",
            title="Road Defect Rectification and Pothole Maintenance Norms (IRC:SP:20)",
            reference_id="IRC:SP:20",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="National and Municipal Roadways",
            verified_at="2026-10-22",
        ),
        text=(
            "Potholes exceeding 25mm depth on arterial or collector roads represent severe transit "
            "hazards and potential vehicular rollover risks. Municipal road engineering divisions "
            "are mandated to erect reflective hazard warning barriers and complete asphalt patching "
            "using bituminous cold/hot mix within 48 to 72 hours of citizen grievance notification."
        ),
    ),
    CivicDocument(
        id="SWM-RULES-2016-MUNICIPAL-DUMP-01",
        category="garbage_and_solid_waste",
        source=DocumentSource(
            authority_name="Ministry of Environment, Forest & Climate Change",
            title="Solid Waste Management Rules 2016 (Rule 15)",
            reference_id="SWM-Rules-2016",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Solid Waste Divisions",
            verified_at="2026-10-22",
        ),
        text=(
            "Under Rule 15 of the Solid Waste Management Rules 2016, municipal local bodies are legally "
            "responsible for daily door-to-door waste collection and preventing unauthorized open dumps. "
            "Accumulated roadside garbage dumps causing public health hazards, odor, and vector breeding "
            "must be cleared and sanitized with disinfectant spray within 24 hours of notification."
        ),
    ),
    CivicDocument(
        id="NLC-PUBLIC-LIGHTING-SLA-01",
        category="streetlighting_infrastructure",
        source=DocumentSource(
            authority_name="Bureau of Energy Efficiency & Urban Municipal Standards",
            title="Municipal Streetlight Maintenance and Illumination Standards",
            reference_id="NLC-Section-Lighting-01",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Public Lighting Divisions",
            verified_at="2026-10-22",
        ),
        text=(
            "Continuous street lighting along pedestrian pathways and vehicular carriageways is mandated "
            "to ensure safety, crime deterrence, and nighttime accident prevention. Reported non-functional "
            "streetlights, damaged wiring, or shattered fixtures must be inspected and restored within 24 to 48 hours."
        ),
    ),
    CivicDocument(
        id="CPHEEO-DRAINAGE-WATERLOGGING-01",
        category="stormwater_and_drainage",
        source=DocumentSource(
            authority_name="Central Public Health & Environmental Engineering Organisation",
            title="Manual on Storm Water Drainage and Waterlogging Mitigation",
            reference_id="CPHEEO-Stormwater-Norms",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Drainage & Sewerage Divisions",
            verified_at="2026-10-22",
        ),
        text=(
            "Standing stormwater on road carriageways accelerates bituminous pavement stripping and subgrade erosion. "
            "Inundated transit corridors posing vehicular stalling or pedestrian risk require immediate deployment of "
            "mobile suction dewatering pumps and drain desilting within 12 to 24 hours of report submission."
        ),
    ),
    CivicDocument(
        id="DISASTER-MGMT-FALLEN-TREE-01",
        category="obstruction_and_horticulture",
        source=DocumentSource(
            authority_name="Urban Disaster Management & Horticulture Department",
            title="Emergency Road Obstruction and Fallen Tree Clearance Protocol",
            reference_id="UDMA-Emergency-Clearance",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Horticulture & Disaster Response",
            verified_at="2026-10-22",
        ),
        text=(
            "Uprooted trees or fallen heavy boughs blocking public rights-of-way, footpaths, or emergency "
            "transit lanes represent critical infrastructure obstructions. Emergency arboriculture units "
            "must deploy mechanical chain-saws to clear debris and restore traffic within 6 to 12 hours."
        ),
    ),
    CivicDocument(
        id="MVA-ILLEGAL-PARKING-REGULATION-01",
        category="illegal_parking_and_traffic",
        source=DocumentSource(
            authority_name="Traffic Police & Municipal Enforcement",
            title="Urban Roadway Obstruction and Illegal Parking Regulations",
            reference_id="MVA-Sec-122-Parking",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Traffic Enforcement & Road Safety",
            verified_at="2026-11-12",
        ),
        text=(
            "Unauthorized vehicle parking on pedestrian footpaths, arterial carriage-ways, or designated emergency corridors "
            "causes severe congestion, blocks emergency access, and forces pedestrians into vehicular traffic. "
            "Municipal traffic enforcement units are empowered to tow obstructing vehicles and issue electronic challans immediately."
        ),
    ),
    CivicDocument(
        id="IRC-67-ROAD-SIGNAGE-MAINTENANCE-01",
        category="broken_road_signs",
        source=DocumentSource(
            authority_name="Indian Roads Congress (IRC)",
            title="Code of Practice for Road Signs & Traffic Control Devices (IRC:67)",
            reference_id="IRC:67-Signage",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Roadways and Traffic Engineering",
            verified_at="2026-11-12",
        ),
        text=(
            "Damaged, obscured, or broken regulatory, warning, and guide signs critically compromise driver decision-making "
            "and increase crash probability at intersections. Highway and urban local bodies must inspect, re-align, "
            "or replace damaged signboards with high-intensity retro-reflective sheeting within 48 hours."
        ),
    ),
    CivicDocument(
        id="MUNICIPAL-VANDALISM-DEFACEMENT-ACT-01",
        category="vandalism_and_graffiti",
        source=DocumentSource(
            authority_name="Municipal Corporation & Public Property Authority",
            title="Prevention of Defacement of Public Property Act Regulations",
            reference_id="Defacement-Act-Sec3",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Infrastructure & Public Asset Protection",
            verified_at="2026-11-12",
        ),
        text=(
            "Unauthorized graffiti, defacement, or vandalism of civic structures, flyover pillars, and public transit shelters "
            "degrades urban aesthetics and signals civil disorder. Municipal maintenance divisions are required to pressure-wash, "
            "re-coat, or restore vandalized public surfaces within 72 hours of verification."
        ),
    ),
    CivicDocument(
        id="VET-SANITATION-DEAD-ANIMAL-DISPOSAL-01",
        category="dead_animal_pollution",
        source=DocumentSource(
            authority_name="Municipal Health & Veterinary Services Department",
            title="Standard Operating Procedure for Safe Carcass Removal and Sanitary Disposal",
            reference_id="Vet-Sanitation-SOP-01",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Sanitation and Public Health",
            verified_at="2026-11-12",
        ),
        text=(
            "Animal carcasses on public thoroughfares cause severe biohazard risks, putrid stench, and pathogen transmission. "
            "Municipal veterinary sanitation flying squads must retrieve, transport in sealed refrigerated vehicles, "
            "and deep-bury or incinerate deceased animals within 6 to 12 hours of complaint registration."
        ),
    ),
    CivicDocument(
        id="CPWD-STRUCTURAL-MAINTENANCE-CONCRETE-01",
        category="damaged_concrete_structures",
        source=DocumentSource(
            authority_name="Central Public Works Department & Structural Safety Cell",
            title="Guidelines for Repair and Rehabilitation of Damaged Concrete Structures",
            reference_id="CPWD-Concrete-Safety-Code",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Civil Engineering and Structural Safety",
            verified_at="2026-11-12",
        ),
        text=(
            "Spalling concrete, exposed corroded rebar, fractured parapets, or structural cracks in public bridges, overpasses, "
            "and retaining walls indicate active structural degradation. Structural engineering teams must immediately cord-off "
            "the perimeter and execute pressure grouting, polymer-modified mortar repair, or micro-concrete jackets."
        ),
    ),
    CivicDocument(
        id="CEA-ELECTRICAL-SAFETY-POLES-WIRES-01",
        category="damaged_electrical_poles_and_wires",
        source=DocumentSource(
            authority_name="Central Electricity Authority (CEA)",
            title="Measures Relating to Safety and Electric Supply Regulations (Regulation 73)",
            reference_id="CEA-Safety-Reg-73",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Power Distribution Utilities & Municipal Engineering",
            verified_at="2026-11-12",
        ),
        text=(
            "Tilted or broken utility poles, low-hanging electrical conductors, or dangling live wires pose lethal electrocution "
            "and fire hazards to commuters. Power distribution licensees and municipal electrical engineers are legally bound "
            "to isolate power immediately upon notification and replace damaged poles and insulators within 12 to 24 hours."
        ),
    ),
    CivicDocument(
        id="CIVICSENSE-REPORTING-CHECKLIST-01",
        category="general_reporting_guidance",
        source=DocumentSource(
            authority_name="CivicSense AI",
            title="Information that helps describe a civic issue",
            reference_id="CivicSense product guidance",
            verification_status=VerificationStatus.GENERAL_GUIDANCE,
            jurisdiction="General guidance; not municipal policy",
        ),
        text=(
            "For a useful report, provide a clear photo, the issue location, a "
            "nearby landmark, and a short description of what is affected. This "
            "is CivicSense product guidance, not an official government rule."
        ),
    ),
]

