--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2026-01-08 22:31:04

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 27810)
-- Name: dev; Type: SCHEMA; Schema: -; Owner: fastapi_user
--

CREATE SCHEMA dev;


ALTER SCHEMA dev OWNER TO fastapi_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 229 (class 1259 OID 27890)
-- Name: client_contracts; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.client_contracts (
    client_profile_id integer NOT NULL,
    contract_number character varying(50) NOT NULL,
    origin_country character varying(50),
    gsa_proposed_discount numeric(5,2),
    q_v_discount character varying(50),
    additional_concessions character varying(50),
    normal_delivery_time integer,
    expedited_delivery_time integer,
    fob_term character varying(50),
    energy_star_compliance character varying(50),
    client_id integer NOT NULL,
    client_company_logo character varying(50),
    signatory_name character varying(128),
    signatory_title character varying(50),
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.client_contracts OWNER TO fastapi_user;

--
-- TOC entry 228 (class 1259 OID 27889)
-- Name: client_contracts_client_profile_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.client_contracts_client_profile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.client_contracts_client_profile_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5045 (class 0 OID 0)
-- Dependencies: 228
-- Name: client_contracts_client_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.client_contracts_client_profile_id_seq OWNED BY dev.client_contracts.client_profile_id;


--
-- TOC entry 225 (class 1259 OID 27844)
-- Name: client_profiles; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.client_profiles (
    client_id integer NOT NULL,
    company_name character varying(30) NOT NULL,
    company_email character varying(50) NOT NULL,
    company_phone_no character varying(15) NOT NULL,
    company_address character varying(50) NOT NULL,
    company_city character varying(50) NOT NULL,
    company_state character varying(50) NOT NULL,
    company_zip character varying(7) NOT NULL,
    contact_officer_name character varying(30) NOT NULL,
    contact_officer_email character varying(50) NOT NULL,
    contact_officer_phone_no character varying(15) NOT NULL,
    contact_officer_address character varying(50) NOT NULL,
    contact_officer_city character varying(50) NOT NULL,
    contact_officer_state character varying(50) NOT NULL,
    contact_officer_zip character varying(7) NOT NULL,
    status integer NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.client_profiles OWNER TO fastapi_user;

--
-- TOC entry 224 (class 1259 OID 27843)
-- Name: client_profiles_client_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.client_profiles_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.client_profiles_client_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5046 (class 0 OID 0)
-- Dependencies: 224
-- Name: client_profiles_client_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.client_profiles_client_id_seq OWNED BY dev.client_profiles.client_id;


--
-- TOC entry 231 (class 1259 OID 27907)
-- Name: cpl_list; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.cpl_list (
    cpl_id integer NOT NULL,
    client_id integer NOT NULL,
    manufacturer_name text NOT NULL,
    manufacturer_part_number text NOT NULL,
    item_name text NOT NULL,
    item_description text,
    commercial_list_price numeric(10,2),
    origin_country text,
    uploaded_by integer NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.cpl_list OWNER TO fastapi_user;

--
-- TOC entry 230 (class 1259 OID 27906)
-- Name: cpl_list_cpl_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.cpl_list_cpl_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.cpl_list_cpl_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5047 (class 0 OID 0)
-- Dependencies: 230
-- Name: cpl_list_cpl_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.cpl_list_cpl_id_seq OWNED BY dev.cpl_list.cpl_id;


--
-- TOC entry 233 (class 1259 OID 27929)
-- Name: file_uploads; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.file_uploads (
    upload_id integer NOT NULL,
    user_id integer NOT NULL,
    client_id integer NOT NULL,
    original_filename text NOT NULL,
    s3_saved_filename text NOT NULL,
    file_size bigint NOT NULL,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    notes text,
    s3_saved_path text NOT NULL,
    uploaded_by integer NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.file_uploads OWNER TO fastapi_user;

--
-- TOC entry 232 (class 1259 OID 27928)
-- Name: file_uploads_upload_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.file_uploads_upload_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.file_uploads_upload_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5048 (class 0 OID 0)
-- Dependencies: 232
-- Name: file_uploads_upload_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.file_uploads_upload_id_seq OWNED BY dev.file_uploads.upload_id;


--
-- TOC entry 235 (class 1259 OID 27957)
-- Name: jobs; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.jobs (
    job_id integer NOT NULL,
    user_id integer NOT NULL,
    client_id integer NOT NULL,
    status integer NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.jobs OWNER TO fastapi_user;

--
-- TOC entry 234 (class 1259 OID 27956)
-- Name: jobs_job_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.jobs_job_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.jobs_job_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5049 (class 0 OID 0)
-- Dependencies: 234
-- Name: jobs_job_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.jobs_job_id_seq OWNED BY dev.jobs.job_id;


--
-- TOC entry 239 (class 1259 OID 27999)
-- Name: modification_action; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.modification_action (
    action_id integer NOT NULL,
    user_id integer NOT NULL,
    client_id integer NOT NULL,
    job_id integer NOT NULL,
    action_type text NOT NULL,
    old_price numeric(10,2),
    new_price numeric(10,2),
    old_description text,
    new_description text,
    number_of_items_impacted integer NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.modification_action OWNER TO fastapi_user;

--
-- TOC entry 238 (class 1259 OID 27998)
-- Name: modification_action_action_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.modification_action_action_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.modification_action_action_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5050 (class 0 OID 0)
-- Dependencies: 238
-- Name: modification_action_action_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.modification_action_action_id_seq OWNED BY dev.modification_action.action_id;


--
-- TOC entry 241 (class 1259 OID 28026)
-- Name: product_dim; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.product_dim (
    dim_id integer NOT NULL,
    product_id integer NOT NULL,
    length numeric(10,2),
    width numeric(10,2),
    height numeric(10,2),
    physical_uom character varying(50),
    weight_lbs numeric(10,2),
    warranty_period integer,
    photo_type character varying(50),
    photo_path character varying(50),
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.product_dim OWNER TO fastapi_user;

--
-- TOC entry 240 (class 1259 OID 28025)
-- Name: product_dim_dim_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.product_dim_dim_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.product_dim_dim_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 240
-- Name: product_dim_dim_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.product_dim_dim_id_seq OWNED BY dev.product_dim.dim_id;


--
-- TOC entry 243 (class 1259 OID 28041)
-- Name: product_history; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.product_history (
    product_history_id integer NOT NULL,
    product_id integer NOT NULL,
    client_id integer NOT NULL,
    item_type character varying(50) NOT NULL,
    item_name character varying(50) NOT NULL,
    item_description text,
    manufacturer character varying(50) NOT NULL,
    manufacturer_part_number character varying(50) NOT NULL,
    client_part_number character varying(50),
    sin character varying(50),
    country_of_origin character varying(50),
    recycled_content_percent numeric(5,2),
    uom character varying(50),
    quantity_per_pack integer,
    quantity_unit_uom character varying(50),
    nsn character varying(50),
    upc character varying(50),
    unspsc character varying(50),
    hazmat character varying(50),
    product_info_code character varying(50),
    url_508 text,
    product_url text,
    effective_start_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    effective_end_date timestamp with time zone,
    is_current boolean DEFAULT true NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.product_history OWNER TO fastapi_user;

--
-- TOC entry 242 (class 1259 OID 28040)
-- Name: product_history_product_history_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.product_history_product_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.product_history_product_history_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5052 (class 0 OID 0)
-- Dependencies: 242
-- Name: product_history_product_history_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.product_history_product_history_id_seq OWNED BY dev.product_history.product_history_id;


--
-- TOC entry 237 (class 1259 OID 27982)
-- Name: product_master; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.product_master (
    product_id integer NOT NULL,
    client_id integer NOT NULL,
    item_type character varying(50) NOT NULL,
    item_name character varying(50) NOT NULL,
    item_description text,
    manufacturer character varying(50) NOT NULL,
    manufacturer_part_number character varying(50) NOT NULL,
    client_part_number character varying(50),
    sin character varying(50),
    commercial_list_price numeric(5,2),
    country_of_origin character varying(50),
    recycled_content_percent numeric(5,2),
    uom character varying(50),
    quantity_per_pack integer,
    quantity_unit_uom character varying(50),
    nsn character varying(50),
    upc character varying(50),
    unspsc character varying(50),
    hazmat character varying(50),
    product_info_code character varying(50),
    url_508 text,
    product_url text,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.product_master OWNER TO fastapi_user;

--
-- TOC entry 236 (class 1259 OID 27981)
-- Name: product_master_product_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.product_master_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.product_master_product_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 236
-- Name: product_master_product_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.product_master_product_id_seq OWNED BY dev.product_master.product_id;


--
-- TOC entry 219 (class 1259 OID 27812)
-- Name: role; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.role (
    role_id integer NOT NULL,
    role_name character varying(10) NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.role OWNER TO fastapi_user;

--
-- TOC entry 218 (class 1259 OID 27811)
-- Name: role_role_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.role_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.role_role_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 218
-- Name: role_role_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.role_role_id_seq OWNED BY dev.role.role_id;


--
-- TOC entry 221 (class 1259 OID 27822)
-- Name: status; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.status (
    status_id integer NOT NULL,
    status_code character varying(10) NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.status OWNER TO fastapi_user;

--
-- TOC entry 220 (class 1259 OID 27821)
-- Name: status_status_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.status_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.status_status_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5055 (class 0 OID 0)
-- Dependencies: 220
-- Name: status_status_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.status_status_id_seq OWNED BY dev.status.status_id;


--
-- TOC entry 223 (class 1259 OID 27832)
-- Name: template_documents; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.template_documents (
    template_id integer NOT NULL,
    name text NOT NULL,
    description text,
    template_type text NOT NULL,
    file_s3_location text NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.template_documents OWNER TO fastapi_user;

--
-- TOC entry 222 (class 1259 OID 27831)
-- Name: template_documents_template_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.template_documents_template_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.template_documents_template_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5056 (class 0 OID 0)
-- Dependencies: 222
-- Name: template_documents_template_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.template_documents_template_id_seq OWNED BY dev.template_documents.template_id;


--
-- TOC entry 227 (class 1259 OID 27869)
-- Name: users; Type: TABLE; Schema: dev; Owner: fastapi_user
--

CREATE TABLE dev.users (
    user_id integer NOT NULL,
    name character varying(30) NOT NULL,
    email character varying(50) NOT NULL,
    phone_no character varying(15) NOT NULL,
    is_active boolean NOT NULL,
    cognito_sub character varying(50) NOT NULL,
    role_id integer NOT NULL,
    created_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE dev.users OWNER TO fastapi_user;

--
-- TOC entry 226 (class 1259 OID 27868)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: dev; Owner: fastapi_user
--

CREATE SEQUENCE dev.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE dev.users_user_id_seq OWNER TO fastapi_user;

--
-- TOC entry 5057 (class 0 OID 0)
-- Dependencies: 226
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: dev; Owner: fastapi_user
--

ALTER SEQUENCE dev.users_user_id_seq OWNED BY dev.users.user_id;


--
-- TOC entry 4771 (class 2604 OID 27893)
-- Name: client_contracts client_profile_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_contracts ALTER COLUMN client_profile_id SET DEFAULT nextval('dev.client_contracts_client_profile_id_seq'::regclass);


--
-- TOC entry 4765 (class 2604 OID 27847)
-- Name: client_profiles client_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles ALTER COLUMN client_id SET DEFAULT nextval('dev.client_profiles_client_id_seq'::regclass);


--
-- TOC entry 4774 (class 2604 OID 27910)
-- Name: cpl_list cpl_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.cpl_list ALTER COLUMN cpl_id SET DEFAULT nextval('dev.cpl_list_cpl_id_seq'::regclass);


--
-- TOC entry 4777 (class 2604 OID 27932)
-- Name: file_uploads upload_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.file_uploads ALTER COLUMN upload_id SET DEFAULT nextval('dev.file_uploads_upload_id_seq'::regclass);


--
-- TOC entry 4781 (class 2604 OID 27960)
-- Name: jobs job_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.jobs ALTER COLUMN job_id SET DEFAULT nextval('dev.jobs_job_id_seq'::regclass);


--
-- TOC entry 4787 (class 2604 OID 28002)
-- Name: modification_action action_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.modification_action ALTER COLUMN action_id SET DEFAULT nextval('dev.modification_action_action_id_seq'::regclass);


--
-- TOC entry 4790 (class 2604 OID 28029)
-- Name: product_dim dim_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_dim ALTER COLUMN dim_id SET DEFAULT nextval('dev.product_dim_dim_id_seq'::regclass);


--
-- TOC entry 4793 (class 2604 OID 28044)
-- Name: product_history product_history_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_history ALTER COLUMN product_history_id SET DEFAULT nextval('dev.product_history_product_history_id_seq'::regclass);


--
-- TOC entry 4784 (class 2604 OID 27985)
-- Name: product_master product_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_master ALTER COLUMN product_id SET DEFAULT nextval('dev.product_master_product_id_seq'::regclass);


--
-- TOC entry 4756 (class 2604 OID 27815)
-- Name: role role_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.role ALTER COLUMN role_id SET DEFAULT nextval('dev.role_role_id_seq'::regclass);


--
-- TOC entry 4759 (class 2604 OID 27825)
-- Name: status status_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.status ALTER COLUMN status_id SET DEFAULT nextval('dev.status_status_id_seq'::regclass);


--
-- TOC entry 4762 (class 2604 OID 27835)
-- Name: template_documents template_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.template_documents ALTER COLUMN template_id SET DEFAULT nextval('dev.template_documents_template_id_seq'::regclass);


--
-- TOC entry 4768 (class 2604 OID 27872)
-- Name: users user_id; Type: DEFAULT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.users ALTER COLUMN user_id SET DEFAULT nextval('dev.users_user_id_seq'::regclass);


--
-- TOC entry 5025 (class 0 OID 27890)
-- Dependencies: 229
-- Data for Name: client_contracts; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.client_contracts (client_profile_id, contract_number, origin_country, gsa_proposed_discount, q_v_discount, additional_concessions, normal_delivery_time, expedited_delivery_time, fob_term, energy_star_compliance, client_id, client_company_logo, signatory_name, signatory_title, created_time, updated_time) FROM stdin;
1	CN-2024-001	USA	15.50	10%	Free shipping	14	7	FOB Shipping Point	Yes	1	logo1.png	John Smith	Director	2026-01-08 22:25:02.195072+05:30	2026-01-08 22:25:02.195072+05:30
2	CN-2024-002	Canada	12.00	8%	Extended warranty	21	10	FOB Destination	No	2	logo2.png	Jane Doe	Manager	2026-01-08 22:25:02.195072+05:30	2026-01-08 22:25:02.195072+05:30
3	CN-2024-003	Mexico	18.75	12%	Volume discount	10	5	FOB Shipping Point	Yes	3	logo3.png	Carlos Lopez	VP Sales	2026-01-08 22:25:02.195072+05:30	2026-01-08 22:25:02.195072+05:30
4	CN-2024-004	USA	20.00	15%	Payment terms	14	7	FOB Destination	Yes	4	logo4.png	Sarah Johnson	Procurement	2026-01-08 22:25:02.195072+05:30	2026-01-08 22:25:02.195072+05:30
5	CN-2024-005	Germany	16.25	11%	Training included	28	14	FOB Shipping Point	No	5	logo5.png	Klaus Mueller	Head	2026-01-08 22:25:02.195072+05:30	2026-01-08 22:25:02.195072+05:30
6	CN-2024-006	UK	19.99	13%	Technical support	21	10	FOB Destination	Yes	6	logo6.png	Emma Wilson	Director	2026-01-08 22:25:02.195072+05:30	2026-01-08 22:25:02.195072+05:30
\.


--
-- TOC entry 5021 (class 0 OID 27844)
-- Dependencies: 225
-- Data for Name: client_profiles; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.client_profiles (client_id, company_name, company_email, company_phone_no, company_address, company_city, company_state, company_zip, contact_officer_name, contact_officer_email, contact_officer_phone_no, contact_officer_address, contact_officer_city, contact_officer_state, contact_officer_zip, status, created_time, updated_time) FROM stdin;
1	Test Company	user@example.com	9123456789	123, colver street	london	E112 3DS	E112 	Teste	user@example.com	string	string	string	string	string	1	2026-01-08 21:02:04.91323+05:30	2026-01-08 21:02:04.91323+05:30
2	Tech Corp	info@techcorp.com	555-0001	123 Tech St	San Francisco	CA	94102	John Smith	john@techcorp.com	555-1001	456 Main Ave	San Francisco	CA	94103	1	2026-01-08 22:22:39.943248+05:30	2026-01-08 22:22:39.943248+05:30
3	Cloud Solutions	contact@cloudsol.com	555-0002	789 Cloud Rd	Seattle	WA	98101	Sarah Johnson	sarah@cloudsol.com	555-1002	321 Cloud Ln	Seattle	WA	98102	1	2026-01-08 22:22:39.943248+05:30	2026-01-08 22:22:39.943248+05:30
4	Data Systems	hello@datasys.com	555-0003	101 Data Dr	Austin	TX	78701	Mike Chen	mike@datasys.com	555-1003	202 Data Ave	Austin	TX	78702	1	2026-01-08 22:22:39.943248+05:30	2026-01-08 22:22:39.943248+05:30
5	Web Innovations	support@webinno.com	555-0004	303 Web Way	Boston	MA	02101	Emily Davis	emily@webinno.com	555-1004	404 Web St	Boston	MA	02102	1	2026-01-08 22:22:39.943248+05:30	2026-01-08 22:22:39.943248+05:30
6	AI Enterprises	admin@aient.com	555-0005	505 AI Ave	New York	NY	10001	Robert Wilson	robert@aient.com	555-1005	606 AI Blvd	New York	NY	10002	1	2026-01-08 22:22:39.943248+05:30	2026-01-08 22:22:39.943248+05:30
\.


--
-- TOC entry 5027 (class 0 OID 27907)
-- Dependencies: 231
-- Data for Name: cpl_list; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.cpl_list (cpl_id, client_id, manufacturer_name, manufacturer_part_number, item_name, item_description, commercial_list_price, origin_country, uploaded_by, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5029 (class 0 OID 27929)
-- Dependencies: 233
-- Data for Name: file_uploads; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.file_uploads (upload_id, user_id, client_id, original_filename, s3_saved_filename, file_size, uploaded_at, notes, s3_saved_path, uploaded_by, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5031 (class 0 OID 27957)
-- Dependencies: 235
-- Data for Name: jobs; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.jobs (job_id, user_id, client_id, status, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5035 (class 0 OID 27999)
-- Dependencies: 239
-- Data for Name: modification_action; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.modification_action (action_id, user_id, client_id, job_id, action_type, old_price, new_price, old_description, new_description, number_of_items_impacted, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5037 (class 0 OID 28026)
-- Dependencies: 241
-- Data for Name: product_dim; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.product_dim (dim_id, product_id, length, width, height, physical_uom, weight_lbs, warranty_period, photo_type, photo_path, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5039 (class 0 OID 28041)
-- Dependencies: 243
-- Data for Name: product_history; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.product_history (product_history_id, product_id, client_id, item_type, item_name, item_description, manufacturer, manufacturer_part_number, client_part_number, sin, country_of_origin, recycled_content_percent, uom, quantity_per_pack, quantity_unit_uom, nsn, upc, unspsc, hazmat, product_info_code, url_508, product_url, effective_start_date, effective_end_date, is_current, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5033 (class 0 OID 27982)
-- Dependencies: 237
-- Data for Name: product_master; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.product_master (product_id, client_id, item_type, item_name, item_description, manufacturer, manufacturer_part_number, client_part_number, sin, commercial_list_price, country_of_origin, recycled_content_percent, uom, quantity_per_pack, quantity_unit_uom, nsn, upc, unspsc, hazmat, product_info_code, url_508, product_url, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5015 (class 0 OID 27812)
-- Dependencies: 219
-- Data for Name: role; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.role (role_id, role_name, created_time, updated_time) FROM stdin;
1	ADMIN	2026-01-08 20:45:30.670701+05:30	2026-01-08 20:45:30.670701+05:30
2	USER	2026-01-08 20:45:30.670701+05:30	2026-01-08 20:45:30.670701+05:30
3	MANAGER	2026-01-08 20:45:30.670701+05:30	2026-01-08 20:45:30.670701+05:30
\.


--
-- TOC entry 5017 (class 0 OID 27822)
-- Dependencies: 221
-- Data for Name: status; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.status (status_id, status_code, created_time, updated_time) FROM stdin;
1	ACTIVE	2026-01-08 20:45:30.670701+05:30	2026-01-08 20:45:30.670701+05:30
2	INACTIVE	2026-01-08 20:45:30.670701+05:30	2026-01-08 20:45:30.670701+05:30
3	ALL	2026-01-08 20:45:30.670701+05:30	2026-01-08 20:45:30.670701+05:30
\.


--
-- TOC entry 5019 (class 0 OID 27832)
-- Dependencies: 223
-- Data for Name: template_documents; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.template_documents (template_id, name, description, template_type, file_s3_location, created_time, updated_time) FROM stdin;
\.


--
-- TOC entry 5023 (class 0 OID 27869)
-- Dependencies: 227
-- Data for Name: users; Type: TABLE DATA; Schema: dev; Owner: fastapi_user
--

COPY dev.users (user_id, name, email, phone_no, is_active, cognito_sub, role_id, created_time, updated_time) FROM stdin;
1	Sreya Gujja	gujjasreya2000@gmail.com	NA	f	d0dc79bc-c051-7024-f1ff-85e43284edf1	2	2026-01-08 20:55:50.71252+05:30	2026-01-08 20:55:50.71252+05:30
\.


--
-- TOC entry 5058 (class 0 OID 0)
-- Dependencies: 228
-- Name: client_contracts_client_profile_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.client_contracts_client_profile_id_seq', 6, true);


--
-- TOC entry 5059 (class 0 OID 0)
-- Dependencies: 224
-- Name: client_profiles_client_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.client_profiles_client_id_seq', 1, true);


--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 230
-- Name: cpl_list_cpl_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.cpl_list_cpl_id_seq', 1, false);


--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 232
-- Name: file_uploads_upload_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.file_uploads_upload_id_seq', 1, false);


--
-- TOC entry 5062 (class 0 OID 0)
-- Dependencies: 234
-- Name: jobs_job_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.jobs_job_id_seq', 1, false);


--
-- TOC entry 5063 (class 0 OID 0)
-- Dependencies: 238
-- Name: modification_action_action_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.modification_action_action_id_seq', 1, false);


--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 240
-- Name: product_dim_dim_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.product_dim_dim_id_seq', 1, false);


--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 242
-- Name: product_history_product_history_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.product_history_product_history_id_seq', 1, false);


--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 236
-- Name: product_master_product_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.product_master_product_id_seq', 1, false);


--
-- TOC entry 5067 (class 0 OID 0)
-- Dependencies: 218
-- Name: role_role_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.role_role_id_seq', 3, true);


--
-- TOC entry 5068 (class 0 OID 0)
-- Dependencies: 220
-- Name: status_status_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.status_status_id_seq', 3, true);


--
-- TOC entry 5069 (class 0 OID 0)
-- Dependencies: 222
-- Name: template_documents_template_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.template_documents_template_id_seq', 1, false);


--
-- TOC entry 5070 (class 0 OID 0)
-- Dependencies: 226
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: dev; Owner: fastapi_user
--

SELECT pg_catalog.setval('dev.users_user_id_seq', 1, true);


--
-- TOC entry 4828 (class 2606 OID 27899)
-- Name: client_contracts client_contracts_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_contracts
    ADD CONSTRAINT client_contracts_pkey PRIMARY KEY (client_profile_id);


--
-- TOC entry 4808 (class 2606 OID 27855)
-- Name: client_profiles client_profiles_company_email_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles
    ADD CONSTRAINT client_profiles_company_email_key UNIQUE (company_email);


--
-- TOC entry 4810 (class 2606 OID 27857)
-- Name: client_profiles client_profiles_company_phone_no_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles
    ADD CONSTRAINT client_profiles_company_phone_no_key UNIQUE (company_phone_no);


--
-- TOC entry 4812 (class 2606 OID 27859)
-- Name: client_profiles client_profiles_contact_officer_email_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles
    ADD CONSTRAINT client_profiles_contact_officer_email_key UNIQUE (contact_officer_email);


--
-- TOC entry 4814 (class 2606 OID 27861)
-- Name: client_profiles client_profiles_contact_officer_phone_no_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles
    ADD CONSTRAINT client_profiles_contact_officer_phone_no_key UNIQUE (contact_officer_phone_no);


--
-- TOC entry 4816 (class 2606 OID 27853)
-- Name: client_profiles client_profiles_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles
    ADD CONSTRAINT client_profiles_pkey PRIMARY KEY (client_id);


--
-- TOC entry 4831 (class 2606 OID 27916)
-- Name: cpl_list cpl_list_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.cpl_list
    ADD CONSTRAINT cpl_list_pkey PRIMARY KEY (cpl_id);


--
-- TOC entry 4834 (class 2606 OID 27939)
-- Name: file_uploads file_uploads_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.file_uploads
    ADD CONSTRAINT file_uploads_pkey PRIMARY KEY (upload_id);


--
-- TOC entry 4838 (class 2606 OID 27964)
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (job_id);


--
-- TOC entry 4844 (class 2606 OID 28008)
-- Name: modification_action modification_action_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.modification_action
    ADD CONSTRAINT modification_action_pkey PRIMARY KEY (action_id);


--
-- TOC entry 4847 (class 2606 OID 28033)
-- Name: product_dim product_dim_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_dim
    ADD CONSTRAINT product_dim_pkey PRIMARY KEY (dim_id);


--
-- TOC entry 4850 (class 2606 OID 28052)
-- Name: product_history product_history_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_history
    ADD CONSTRAINT product_history_pkey PRIMARY KEY (product_history_id);


--
-- TOC entry 4841 (class 2606 OID 27991)
-- Name: product_master product_master_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_master
    ADD CONSTRAINT product_master_pkey PRIMARY KEY (product_id);


--
-- TOC entry 4800 (class 2606 OID 27819)
-- Name: role role_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (role_id);


--
-- TOC entry 4803 (class 2606 OID 27829)
-- Name: status status_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (status_id);


--
-- TOC entry 4806 (class 2606 OID 27841)
-- Name: template_documents template_documents_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.template_documents
    ADD CONSTRAINT template_documents_pkey PRIMARY KEY (template_id);


--
-- TOC entry 4820 (class 2606 OID 27882)
-- Name: users users_cognito_sub_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.users
    ADD CONSTRAINT users_cognito_sub_key UNIQUE (cognito_sub);


--
-- TOC entry 4822 (class 2606 OID 27878)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4824 (class 2606 OID 27880)
-- Name: users users_phone_no_key; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.users
    ADD CONSTRAINT users_phone_no_key UNIQUE (phone_no);


--
-- TOC entry 4826 (class 2606 OID 27876)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 4829 (class 1259 OID 27905)
-- Name: ix_client_contracts_client_profile_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_client_contracts_client_profile_id ON dev.client_contracts USING btree (client_profile_id);


--
-- TOC entry 4817 (class 1259 OID 27867)
-- Name: ix_client_profiles_client_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_client_profiles_client_id ON dev.client_profiles USING btree (client_id);


--
-- TOC entry 4832 (class 1259 OID 27927)
-- Name: ix_cpl_list_cpl_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_cpl_list_cpl_id ON dev.cpl_list USING btree (cpl_id);


--
-- TOC entry 4835 (class 1259 OID 27955)
-- Name: ix_file_uploads_upload_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_file_uploads_upload_id ON dev.file_uploads USING btree (upload_id);


--
-- TOC entry 4836 (class 1259 OID 27980)
-- Name: ix_jobs_job_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_jobs_job_id ON dev.jobs USING btree (job_id);


--
-- TOC entry 4842 (class 1259 OID 28024)
-- Name: ix_modification_action_action_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_modification_action_action_id ON dev.modification_action USING btree (action_id);


--
-- TOC entry 4845 (class 1259 OID 28039)
-- Name: ix_product_dim_dim_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_product_dim_dim_id ON dev.product_dim USING btree (dim_id);


--
-- TOC entry 4848 (class 1259 OID 28063)
-- Name: ix_product_history_product_history_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_product_history_product_history_id ON dev.product_history USING btree (product_history_id);


--
-- TOC entry 4839 (class 1259 OID 27997)
-- Name: ix_product_master_product_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_product_master_product_id ON dev.product_master USING btree (product_id);


--
-- TOC entry 4798 (class 1259 OID 27820)
-- Name: ix_role_role_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_role_role_id ON dev.role USING btree (role_id);


--
-- TOC entry 4801 (class 1259 OID 27830)
-- Name: ix_status_status_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_status_status_id ON dev.status USING btree (status_id);


--
-- TOC entry 4804 (class 1259 OID 27842)
-- Name: ix_template_documents_template_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_template_documents_template_id ON dev.template_documents USING btree (template_id);


--
-- TOC entry 4818 (class 1259 OID 27888)
-- Name: ix_users_user_id; Type: INDEX; Schema: dev; Owner: fastapi_user
--

CREATE INDEX ix_users_user_id ON dev.users USING btree (user_id);


--
-- TOC entry 4853 (class 2606 OID 27900)
-- Name: client_contracts client_contracts_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_contracts
    ADD CONSTRAINT client_contracts_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4851 (class 2606 OID 27862)
-- Name: client_profiles client_profiles_status_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.client_profiles
    ADD CONSTRAINT client_profiles_status_fkey FOREIGN KEY (status) REFERENCES dev.status(status_id) ON DELETE RESTRICT;


--
-- TOC entry 4854 (class 2606 OID 27917)
-- Name: cpl_list cpl_list_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.cpl_list
    ADD CONSTRAINT cpl_list_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4855 (class 2606 OID 27922)
-- Name: cpl_list cpl_list_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.cpl_list
    ADD CONSTRAINT cpl_list_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES dev.users(user_id) ON DELETE RESTRICT;


--
-- TOC entry 4856 (class 2606 OID 27945)
-- Name: file_uploads file_uploads_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.file_uploads
    ADD CONSTRAINT file_uploads_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4857 (class 2606 OID 27950)
-- Name: file_uploads file_uploads_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.file_uploads
    ADD CONSTRAINT file_uploads_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES dev.users(user_id) ON DELETE RESTRICT;


--
-- TOC entry 4858 (class 2606 OID 27940)
-- Name: file_uploads file_uploads_user_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.file_uploads
    ADD CONSTRAINT file_uploads_user_id_fkey FOREIGN KEY (user_id) REFERENCES dev.users(user_id) ON DELETE RESTRICT;


--
-- TOC entry 4859 (class 2606 OID 27970)
-- Name: jobs jobs_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.jobs
    ADD CONSTRAINT jobs_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4860 (class 2606 OID 27975)
-- Name: jobs jobs_status_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.jobs
    ADD CONSTRAINT jobs_status_fkey FOREIGN KEY (status) REFERENCES dev.status(status_id) ON DELETE RESTRICT;


--
-- TOC entry 4861 (class 2606 OID 27965)
-- Name: jobs jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.jobs
    ADD CONSTRAINT jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES dev.users(user_id) ON DELETE RESTRICT;


--
-- TOC entry 4863 (class 2606 OID 28014)
-- Name: modification_action modification_action_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.modification_action
    ADD CONSTRAINT modification_action_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4864 (class 2606 OID 28019)
-- Name: modification_action modification_action_job_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.modification_action
    ADD CONSTRAINT modification_action_job_id_fkey FOREIGN KEY (job_id) REFERENCES dev.jobs(job_id) ON DELETE CASCADE;


--
-- TOC entry 4865 (class 2606 OID 28009)
-- Name: modification_action modification_action_user_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.modification_action
    ADD CONSTRAINT modification_action_user_id_fkey FOREIGN KEY (user_id) REFERENCES dev.users(user_id) ON DELETE RESTRICT;


--
-- TOC entry 4866 (class 2606 OID 28034)
-- Name: product_dim product_dim_product_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_dim
    ADD CONSTRAINT product_dim_product_id_fkey FOREIGN KEY (product_id) REFERENCES dev.product_master(product_id) ON DELETE CASCADE;


--
-- TOC entry 4867 (class 2606 OID 28058)
-- Name: product_history product_history_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_history
    ADD CONSTRAINT product_history_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4868 (class 2606 OID 28053)
-- Name: product_history product_history_product_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_history
    ADD CONSTRAINT product_history_product_id_fkey FOREIGN KEY (product_id) REFERENCES dev.product_master(product_id) ON DELETE CASCADE;


--
-- TOC entry 4862 (class 2606 OID 27992)
-- Name: product_master product_master_client_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.product_master
    ADD CONSTRAINT product_master_client_id_fkey FOREIGN KEY (client_id) REFERENCES dev.client_profiles(client_id) ON DELETE RESTRICT;


--
-- TOC entry 4852 (class 2606 OID 27883)
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: dev; Owner: fastapi_user
--

ALTER TABLE ONLY dev.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES dev.role(role_id) ON DELETE RESTRICT;


-- Completed on 2026-01-08 22:31:05

--
-- PostgreSQL database dump complete
--

