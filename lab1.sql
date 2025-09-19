--
-- PostgreSQL database dump
--

\restrict sRRQRthThafOfww74fCvJRPfpoxBFgi7HcBFk24r5x9MOgAGibL7gD9QnCj42rT

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-09-19 16:30:14

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
-- TOC entry 219 (class 1259 OID 16602)
-- Name: reminder; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reminder (
    reminder_id integer NOT NULL,
    entry_id integer NOT NULL,
    remind_at timestamp without time zone NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.reminder OWNER TO postgres;

--
-- TOC entry 4793 (class 0 OID 16602)
-- Dependencies: 219
-- Data for Name: reminder; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reminder (reminder_id, entry_id, remind_at, active) FROM stdin;
1	2	2025-09-18 19:00:00	t
2	3	2025-09-19 19:00:00	f
\.


--
-- TOC entry 4646 (class 2606 OID 16606)
-- Name: reminder reminder_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminder
    ADD CONSTRAINT reminder_pkey PRIMARY KEY (reminder_id);


--
-- TOC entry 4647 (class 2606 OID 16612)
-- Name: reminder reminder_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminder
    ADD CONSTRAINT reminder_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES public.entry(entry_id) NOT VALID;


-- Completed on 2025-09-19 16:30:14

--
-- PostgreSQL database dump complete
--

\unrestrict sRRQRthThafOfww74fCvJRPfpoxBFgi7HcBFk24r5x9MOgAGibL7gD9QnCj42rT

