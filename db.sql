-- =========================================
-- BEGIN: WINVALE AUTOMATION DATABASE MODEL
-- =========================================

CREATE TABLE Clients (
    client_id UUID PRIMARY KEY,
    client_name VARCHAR(255),
    duns_number VARCHAR(20),
    cage_code VARCHAR(20),
    uei_number VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    poc_name VARCHAR(255),
    poc_email VARCHAR(255),
    poc_phone VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE Contracts (
    contract_id UUID PRIMARY KEY,
    client_id UUID REFERENCES Clients(client_id),
    contract_number VARCHAR(100),
    solicitation_number VARCHAR(100),
    refresh_number VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE Contract_Settings (
    settings_id UUID PRIMARY KEY,
    contract_id UUID REFERENCES Contracts(contract_id),
    standard_discount DECIMAL(10,2),
    quantity_discount VARCHAR(255),
    epa_clause VARCHAR(255),
    tdr_indicator BOOLEAN,
    csp_indicator BOOLEAN,
    fob_terms VARCHAR(100),
    delivery_normal VARCHAR(50),
    delivery_expedited VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE Contract_SINs (
    sin_id UUID PRIMARY KEY,
    contract_id UUID REFERENCES Contracts(contract_id),
    sin_code VARCHAR(50)
);

CREATE TABLE Products (
    product_id UUID PRIMARY KEY,
    contract_id UUID REFERENCES Contracts(contract_id),
    manufacturer VARCHAR(255),
    manufacturer_part_number VARCHAR(255),
    product_name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE Product_Prices (
    price_id UUID PRIMARY KEY,
    product_id UUID REFERENCES Products(product_id),
    price DECIMAL(12,2),
    price_type VARCHAR(50), -- GSA / Commercial / IFF included etc.
    effective_date TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE Product_Attributes (
    attribute_id UUID PRIMARY KEY,
    product_id UUID REFERENCES Products(product_id),
    attributes JSONB,
    created_at TIMESTAMP
);

CREATE TABLE CPL_Versions (
    cpl_version_id UUID PRIMARY KEY,
    client_id UUID REFERENCES Clients(client_id),
    file_name VARCHAR(255),
    file_path VARCHAR(255),
    uploaded_by UUID,
    status VARCHAR(50),
    created_at TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE TABLE CPL_Items (
    cpl_item_id UUID PRIMARY KEY,
    cpl_version_id UUID REFERENCES CPL_Versions(cpl_version_id),
    manufacturer VARCHAR(255),
    part_number VARCHAR(255),
    product_name VARCHAR(255),
    description TEXT,
    unit_of_issue VARCHAR(50),
    commercial_price DECIMAL(12,2),
    msrp_price DECIMAL(12,2),
    country_of_origin VARCHAR(100),
    quantity_per_pack INT,
    raw_data JSONB,
    created_at TIMESTAMP
);

CREATE TABLE Modifications (
    modification_id UUID PRIMARY KEY,
    contract_id UUID REFERENCES Contracts(contract_id),
    modification_type VARCHAR(50), -- ADD / DELETE / PRICE_INCREASE / PRICE_DECREASE / DESC_CHANGE
    created_at TIMESTAMP
);

CREATE TABLE Modification_Items (
    mod_item_id UUID PRIMARY KEY,
    modification_id UUID REFERENCES Modifications(modification_id),
    product_id UUID,
    cpl_item_id UUID,
    created_at TIMESTAMP
);

CREATE TABLE Modification_Actions (
    action_id UUID PRIMARY KEY,
    mod_item_id UUID REFERENCES Modification_Items(mod_item_id),
    field_changed VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    created_at TIMESTAMP
);

CREATE TABLE Modification_Workflow (
    workflow_id UUID PRIMARY KEY,
    modification_id UUID REFERENCES Modifications(modification_id),
    status VARCHAR(50), -- PENDING / APPROVED / REJECTED
    reviewed_by UUID,
    reviewed_at TIMESTAMP
);

CREATE TABLE Roles (
    role_id UUID PRIMARY KEY,
    role_name VARCHAR(100)
);

CREATE TABLE Users (
    user_id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255),
    password_hash TEXT,
    role_id UUID REFERENCES Roles(role_id),
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE User_Actions_Log (
    log_id UUID PRIMARY KEY,
    user_id UUID REFERENCES Users(user_id),
    action_type VARCHAR(255),
    details JSONB,
    created_at TIMESTAMP
);

CREATE TABLE Files (
    file_id UUID PRIMARY KEY,
    file_name VARCHAR(255),
    file_path VARCHAR(255),
    uploaded_by UUID REFERENCES Users(user_id),
    uploaded_at TIMESTAMP
);

CREATE TABLE File_Links (
    link_id UUID PRIMARY KEY,
    file_id UUID REFERENCES Files(file_id),
    parent_type VARCHAR(50), -- contract / modification / cpl
    parent_id UUID,
    created_at TIMESTAMP
);

-- =========================================
-- END: WINVALE AUTOMATION DATABASE MODEL
-- =========================================
