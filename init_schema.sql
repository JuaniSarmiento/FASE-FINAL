--
-- PostgreSQL database dump
--

\restrict I1knXb06HZ43V5NO41e9mV00QuxXKd4Pctnf5vavhhUVfabiIhw1Qneqo2U903U

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    id character varying NOT NULL,
    course_id character varying NOT NULL,
    title character varying NOT NULL,
    description character varying,
    type character varying NOT NULL,
    status character varying,
    "order" integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    teacher_id character varying DEFAULT 'default_teacher'::character varying
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- Name: activity_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_assignments (
    id character varying NOT NULL,
    activity_id character varying NOT NULL,
    student_id character varying NOT NULL,
    assigned_at timestamp without time zone
);


ALTER TABLE public.activity_assignments OWNER TO postgres;

--
-- Name: activity_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_documents (
    id character varying NOT NULL,
    activity_id character varying NOT NULL,
    filename character varying NOT NULL,
    content_text character varying,
    embedding_id character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.activity_documents OWNER TO postgres;

--
-- Name: cognitive_traces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cognitive_traces (
    id character varying NOT NULL,
    session_id character varying NOT NULL,
    inferred_state character varying,
    confidence double precision,
    detected_at timestamp without time zone
);


ALTER TABLE public.cognitive_traces OWNER TO postgres;

--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courses (
    id character varying NOT NULL,
    subject_id character varying NOT NULL,
    year integer NOT NULL,
    semester integer NOT NULL,
    active boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: enrollments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enrollments (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    course_id character varying,
    status character varying,
    enrolled_at timestamp without time zone,
    module_id character varying(36)
);


ALTER TABLE public.enrollments OWNER TO postgres;

--
-- Name: exercise_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise_attempts (
    id character varying NOT NULL,
    submission_id character varying NOT NULL,
    exercise_id character varying NOT NULL,
    code_submitted text NOT NULL,
    is_passing boolean,
    execution_output text,
    error_message text,
    created_at timestamp without time zone,
    grade double precision
);


ALTER TABLE public.exercise_attempts OWNER TO postgres;

--
-- Name: exercises; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercises (
    id character varying NOT NULL,
    activity_id character varying NOT NULL,
    title character varying NOT NULL,
    problem_statement character varying NOT NULL,
    starter_code character varying NOT NULL,
    difficulty character varying NOT NULL,
    language character varying NOT NULL,
    status character varying,
    test_cases_json character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    solution_code character varying
);


ALTER TABLE public.exercises OWNER TO postgres;

--
-- Name: incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.incidents (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    incident_type character varying NOT NULL,
    description text NOT NULL,
    severity character varying,
    status character varying,
    created_at timestamp without time zone,
    resolved_at timestamp without time zone,
    resolution_notes text
);


ALTER TABLE public.incidents OWNER TO postgres;

--
-- Name: risk_analyses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.risk_analyses (
    id character varying NOT NULL,
    submission_id character varying NOT NULL,
    risk_score integer NOT NULL,
    risk_level character varying NOT NULL,
    diagnosis text,
    evidence jsonb,
    teacher_advice text,
    positive_aspects jsonb,
    analyzed_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.risk_analyses OWNER TO postgres;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    activity_id character varying NOT NULL,
    status character varying,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: sessions_v2; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions_v2 (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    activity_id character varying NOT NULL,
    status character varying,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.sessions_v2 OWNER TO postgres;

--
-- Name: subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjects (
    id character varying NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    description character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.subjects OWNER TO postgres;

--
-- Name: submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.submissions (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    activity_id character varying NOT NULL,
    status character varying,
    final_score double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.submissions OWNER TO postgres;

--
-- Name: tutor_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tutor_messages (
    id character varying NOT NULL,
    session_id character varying NOT NULL,
    role character varying NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.tutor_messages OWNER TO postgres;

--
-- Name: tutor_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tutor_sessions (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    created_at timestamp without time zone,
    status character varying
);


ALTER TABLE public.tutor_sessions OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id character varying NOT NULL,
    email character varying NOT NULL,
    username character varying,
    hashed_password character varying NOT NULL,
    full_name character varying,
    roles character varying[],
    is_active boolean,
    is_verified boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: activity_assignments activity_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_assignments
    ADD CONSTRAINT activity_assignments_pkey PRIMARY KEY (id);


--
-- Name: activity_documents activity_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_documents
    ADD CONSTRAINT activity_documents_pkey PRIMARY KEY (id);


--
-- Name: cognitive_traces cognitive_traces_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cognitive_traces
    ADD CONSTRAINT cognitive_traces_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (id);


--
-- Name: exercise_attempts exercise_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_attempts
    ADD CONSTRAINT exercise_attempts_pkey PRIMARY KEY (id);


--
-- Name: exercises exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: risk_analyses risk_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_analyses
    ADD CONSTRAINT risk_analyses_pkey PRIMARY KEY (id);


--
-- Name: risk_analyses risk_analyses_submission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_analyses
    ADD CONSTRAINT risk_analyses_submission_id_key UNIQUE (submission_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sessions_v2 sessions_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions_v2
    ADD CONSTRAINT sessions_v2_pkey PRIMARY KEY (id);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: tutor_messages tutor_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tutor_messages
    ADD CONSTRAINT tutor_messages_pkey PRIMARY KEY (id);


--
-- Name: tutor_sessions tutor_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tutor_sessions
    ADD CONSTRAINT tutor_sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_activities_course_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_course_id ON public.activities USING btree (course_id);


--
-- Name: ix_activities_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activities_teacher_id ON public.activities USING btree (teacher_id);


--
-- Name: ix_activity_assignments_activity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_assignments_activity_id ON public.activity_assignments USING btree (activity_id);


--
-- Name: ix_activity_assignments_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_assignments_student_id ON public.activity_assignments USING btree (student_id);


--
-- Name: ix_activity_documents_activity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_documents_activity_id ON public.activity_documents USING btree (activity_id);


--
-- Name: ix_incidents_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_student_id ON public.incidents USING btree (student_id);


--
-- Name: ix_sessions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_student_id ON public.sessions USING btree (student_id);


--
-- Name: ix_sessions_v2_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_v2_student_id ON public.sessions_v2 USING btree (student_id);


--
-- Name: ix_subjects_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_subjects_code ON public.subjects USING btree (code);


--
-- Name: ix_subjects_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subjects_name ON public.subjects USING btree (name);


--
-- Name: ix_submissions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_submissions_student_id ON public.submissions USING btree (student_id);


--
-- Name: ix_tutor_sessions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tutor_sessions_student_id ON public.tutor_sessions USING btree (student_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: activity_assignments activity_assignments_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_assignments
    ADD CONSTRAINT activity_assignments_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: activity_assignments activity_assignments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_assignments
    ADD CONSTRAINT activity_assignments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id);


--
-- Name: activity_documents activity_documents_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_documents
    ADD CONSTRAINT activity_documents_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: cognitive_traces cognitive_traces_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cognitive_traces
    ADD CONSTRAINT cognitive_traces_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: courses courses_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: enrollments enrollments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: enrollments enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id);


--
-- Name: exercise_attempts exercise_attempts_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_attempts
    ADD CONSTRAINT exercise_attempts_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercises(id);


--
-- Name: exercise_attempts exercise_attempts_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise_attempts
    ADD CONSTRAINT exercise_attempts_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- Name: exercises exercises_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: risk_analyses risk_analyses_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_analyses
    ADD CONSTRAINT risk_analyses_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- Name: sessions sessions_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: sessions_v2 sessions_v2_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions_v2
    ADD CONSTRAINT sessions_v2_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: submissions submissions_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- Name: tutor_messages tutor_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tutor_messages
    ADD CONSTRAINT tutor_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- PostgreSQL database dump complete
--

\unrestrict I1knXb06HZ43V5NO41e9mV00QuxXKd4Pctnf5vavhhUVfabiIhw1Qneqo2U903U

