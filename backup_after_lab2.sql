--
-- PostgreSQL database dump
--

\restrict ElPDyP2i2yoB9SNQt1DUicFF3phne9fdZt1kLFeNbuUFzXftGnpagO5bM2Oz1FS

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-12-01 22:57:58

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 24625)
-- Name: audit_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_log (
    log_id integer NOT NULL,
    user_id integer,
    action_type character varying(20),
    description text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.audit_log OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24624)
-- Name: audit_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_log_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_log_log_id_seq OWNER TO postgres;

--
-- TOC entry 4806 (class 0 OID 0)
-- Dependencies: 220
-- Name: audit_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_log_log_id_seq OWNED BY public.audit_log.log_id;


--
-- TOC entry 4650 (class 2604 OID 24628)
-- Name: audit_log log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN log_id SET DEFAULT nextval('public.audit_log_log_id_seq'::regclass);


--
-- TOC entry 4800 (class 0 OID 24625)
-- Dependencies: 221
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_log (log_id, user_id, action_type, description, created_at) FROM stdin;
1	5	UPDATE	Зміна даних: Updated_User_5 -> Updated_User_5	2025-12-01 21:21:09.948265
2	10	DELETE	Користувача видалено. Його записи: 	2025-12-01 21:21:58.122939
3	5	UPDATE	Зміна даних: Updated_User_5 -> Name_Changed_ByOther	2025-12-01 22:27:53.874417
4	5	UPDATE	Зміна даних: Name_Changed_ByOther -> Serial_User_A	2025-12-01 22:29:00.676745
5	5	UPDATE	Зміна даних: Serial_User_A -> prob	2025-12-01 22:32:11.724124
6	5	UPDATE	Зміна даних: prob -> Serial_User_B	2025-12-01 22:33:03.012135
7	5	UPDATE	Зміна даних: Serial_User_B -> Name_Change_ByA	2025-12-01 22:36:16.485445
8	5	UPDATE	Зміна даних: Name_Change_ByA -> Name_Repeatable	2025-12-01 22:39:11.635977
9	5	UPDATE	Зміна даних: Name_Repeatable -> Serial_User_B	2025-12-01 22:42:31.262869
\.


--
-- TOC entry 4807 (class 0 OID 0)
-- Dependencies: 220
-- Name: audit_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_log_log_id_seq', 9, true);


--
-- TOC entry 4653 (class 2606 OID 24633)
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (log_id);


-- Completed on 2025-12-01 22:57:58

--
-- PostgreSQL database dump complete
--

\unrestrict ElPDyP2i2yoB9SNQt1DUicFF3phne9fdZt1kLFeNbuUFzXftGnpagO5bM2Oz1FS

