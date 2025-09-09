--
-- PostgreSQL database dump
--

\restrict 2flBCVgvb6cBFfbRZYMF1CTwiuiQBBZHkoMmai3c38qp85IQIoDMyQjqGunN8a2

-- Dumped from database version 15.14
-- Dumped by pg_dump version 17.6

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
-- Name: evaluations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evaluations (
    evaluate_id integer NOT NULL,
    workflow_id uuid NOT NULL,
    evaluator_id integer NOT NULL,
    score smallint,
    comment text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    evaluation_file text,
    CONSTRAINT evaluations_score_check CHECK (((score >= 0) AND (score <= 100)))
);


ALTER TABLE public.evaluations OWNER TO postgres;

--
-- Name: evaluations_evaluate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.evaluations_evaluate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.evaluations_evaluate_id_seq OWNER TO postgres;

--
-- Name: evaluations_evaluate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.evaluations_evaluate_id_seq OWNED BY public.evaluations.evaluate_id;


--
-- Name: forms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forms (
    form_id uuid NOT NULL,
    workflow_id uuid NOT NULL,
    step_no integer NOT NULL,
    submitter_id integer NOT NULL,
    image_url text,
    image_meta jsonb,
    image_desc text,
    image_desc_file text,
    restoration_opinion text,
    opinion_tags character varying[],
    opinion_file text,
    remark text,
    attachment text,
    is_rollback_from uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE public.forms OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    role_id integer NOT NULL,
    role_key character varying(20) NOT NULL,
    role_name character varying(50) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_role_id_seq OWNER TO postgres;

--
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;


--
-- Name: rollback_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rollback_requests (
    rollback_id integer NOT NULL,
    workflow_id uuid NOT NULL,
    requester_id integer NOT NULL,
    target_form_id uuid NOT NULL,
    reason text NOT NULL,
    status character varying(20),
    approver_id integer,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    support_file_url text,
    deleted_at timestamp with time zone
);


ALTER TABLE public.rollback_requests OWNER TO postgres;

--
-- Name: rollback_requests_rollback_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rollback_requests_rollback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rollback_requests_rollback_id_seq OWNER TO postgres;

--
-- Name: rollback_requests_rollback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rollback_requests_rollback_id_seq OWNED BY public.rollback_requests.rollback_id;


--
-- Name: step_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.step_logs (
    step_log_id integer NOT NULL,
    form_id uuid NOT NULL,
    action character varying(20) NOT NULL,
    operator_id integer NOT NULL,
    comment text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.step_logs OWNER TO postgres;

--
-- Name: step_logs_step_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.step_logs_step_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.step_logs_step_log_id_seq OWNER TO postgres;

--
-- Name: step_logs_step_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.step_logs_step_log_id_seq OWNED BY public.step_logs.step_log_id;


--
-- Name: system_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_configs (
    config_key character varying(50) NOT NULL,
    config_value text,
    description character varying(255),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.system_configs OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(100) NOT NULL,
    role_id integer NOT NULL,
    email character varying(100),
    phone character varying(20),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: workflows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflows (
    workflow_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    initiator_id integer NOT NULL,
    current_step integer,
    status character varying(20),
    is_finalized boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp without time zone
);


ALTER TABLE public.workflows OWNER TO postgres;

--
-- Name: evaluations evaluate_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluations ALTER COLUMN evaluate_id SET DEFAULT nextval('public.evaluations_evaluate_id_seq'::regclass);


--
-- Name: roles role_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);


--
-- Name: rollback_requests rollback_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rollback_requests ALTER COLUMN rollback_id SET DEFAULT nextval('public.rollback_requests_rollback_id_seq'::regclass);


--
-- Name: step_logs step_log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.step_logs ALTER COLUMN step_log_id SET DEFAULT nextval('public.step_logs_step_log_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: evaluations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evaluations (evaluate_id, workflow_id, evaluator_id, score, comment, created_at, updated_at, evaluation_file) FROM stdin;
1	161251f8-2c78-4220-ab36-bc8622bb71a8	1	3	123123	2025-09-01 07:00:47.505977+00	2025-09-01 07:00:47.505977+00	\N
2	5d952765-cce8-4cab-8db1-ffeb0096b3dd	1	89	h	2025-09-03 12:45:55.560672+00	2025-09-03 12:45:55.560672+00	\N
3	47b650e5-233f-49ef-ae20-48706e5aeead	1	99	rt	2025-09-03 13:00:43.401971+00	2025-09-03 13:00:43.401971+00	http://localhost:9000/repair-file/2025/09/03/99282556-a864-4e34-a8de-4adeb55e98cb_20250903_210043.txt
4	90b489ba-912f-42e0-a257-e364ebd2e131	1	77	2	2025-09-03 13:04:57.904509+00	2025-09-03 13:04:57.904509+00	\N
5	26f1d627-5407-4c5d-b203-74dbf745d10a	3	44	555	2025-09-08 08:16:16.487489+00	2025-09-08 08:16:16.487489+00	http://localhost:9000/repair-file/2025/09/08/13a00b89-a2bb-4286-a0f7-9707ee108521_20250908_161616.png
6	f4e4032c-bd7f-4345-b455-082963339c74	3	90	好，这是测试	2025-09-08 15:39:00.244498+00	2025-09-08 15:39:00.244498+00	http://localhost:9000/repair-file/2025/09/08/7499ecab-32e5-4c9a-b15c-e1f21f852b38_20250908_233900.txt
\.


--
-- Data for Name: forms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forms (form_id, workflow_id, step_no, submitter_id, image_url, image_meta, image_desc, image_desc_file, restoration_opinion, opinion_tags, opinion_file, remark, attachment, is_rollback_from, created_at, updated_at, deleted_at) FROM stdin;
ae72b18f-49d1-4109-af5f-2fa7f2e6e935	063d8e8c-d67b-4bb9-819b-b0e22b27677d	1	1	http://localhost:9000/repair-file/2025/09/01/e317d996-b496-4704-95ac-93b183003135_20250901_145813.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123213	\N	123	\N	\N	313	\N	\N	2025-09-01 06:58:13.763678+00	2025-09-01 14:01:03.466415+00	\N
b3973eb7-d406-44ac-b754-a9812308d2f9	161251f8-2c78-4220-ab36-bc8622bb71a8	1	2	http://localhost:9000/repair-file/2025/09/01/3e1e990c-c9f0-4a40-95a6-e26dba598f10_20250901_145921.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123232	\N	123113	\N	\N	1232	\N	\N	2025-09-01 06:59:21.511438+00	2025-09-01 14:01:03.466415+00	\N
40f34d5d-7710-4322-a9d4-0fcfc6d9b3f6	063d8e8c-d67b-4bb9-819b-b0e22b27677d	2	1	http://localhost:9000/repair-file/2025/09/01/e10cc6d5-65c7-4d27-ace7-113fca23337d_20250901_150110.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123123	\N	12323	\N	\N	123231	\N	\N	2025-09-01 07:01:10.445275+00	2025-09-01 14:01:03.466415+00	\N
dd434189-4bf6-48f8-b0b3-b10aed2a613e	063d8e8c-d67b-4bb9-819b-b0e22b27677d	3	1	http://localhost:9000/repair-file/2025/09/01/5c6cc0a4-0ddf-40a4-954d-3eb8a0d7abb6_20250901_150127.jpg	{"size": 580478, "filename": "test.jpg", "content_type": "image/jpeg"}	\N	\N	123	\N	\N	231123	\N	\N	2025-09-01 07:01:27.926939+00	2025-09-01 14:01:03.466415+00	\N
17ad28e5-628d-4a3a-a9c7-db075e65c67f	5d952765-cce8-4cab-8db1-ffeb0096b3dd	1	2	http://localhost:9000/repair-file/2025/09/01/d38529e7-811d-4869-ba95-5540adc95f25_20250901_150739.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	\N	\N	12323	\N	\N	123123	\N	\N	2025-09-01 07:07:39.210387+00	2025-09-01 14:01:03.466415+00	\N
ea83f02f-d94d-487f-800d-d8b4d5237399	5d952765-cce8-4cab-8db1-ffeb0096b3dd	2	2	http://localhost:9000/repair-file/2025/09/01/8e0b8939-1386-47bf-b2e9-bae0404af44e_20250901_151920.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	323	\N	311231	\N	\N	131231	\N	\N	2025-09-01 07:19:20.46513+00	2025-09-01 14:01:03.466415+00	\N
59f085e1-0e1a-4e68-a14d-94634b72a64a	5d952765-cce8-4cab-8db1-ffeb0096b3dd	3	2	http://localhost:9000/repair-file/2025/09/01/d38529e7-811d-4869-ba95-5540adc95f25_20250901_150739.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	\N	\N	12323	\N	\N	123123	\N	17ad28e5-628d-4a3a-a9c7-db075e65c67f	2025-09-01 07:20:56.126515+00	2025-09-01 14:01:03.466415+00	\N
37b79bae-3876-464b-b6d7-bd622735ab2f	5d952765-cce8-4cab-8db1-ffeb0096b3dd	4	2	http://localhost:9000/repair-file/2025/09/01/d38529e7-811d-4869-ba95-5540adc95f25_20250901_150739.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	\N	\N	12323	\N	\N	123123	\N	17ad28e5-628d-4a3a-a9c7-db075e65c67f	2025-09-01 07:21:48.456583+00	2025-09-01 14:01:03.466415+00	\N
a32e3fb0-bd5f-4e32-9174-e488d9539d01	9d2505ce-b469-4345-a7c9-e9e425c941b1	1	2	http://localhost:9000/repair-file/2025/09/01/5c8e7fd5-c73a-4b31-a725-2c39d791c24a_20250901_152357.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123312332231123	\N	2133歌功颂德第三个	\N	\N	戚薇戚薇戚薇	\N	\N	2025-09-01 07:23:57.770242+00	2025-09-01 14:01:03.466415+00	\N
8d31fa92-a873-46ac-9812-ece9b0c7f1cf	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	2	http://localhost:9000/repair-file/2025/09/01/f283f3d2-cb7d-4ab9-aeba-e9841ee63166_20250901_152412.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	各位电饭锅所发生的防守打法	\N	12333	\N	\N	11132312	\N	\N	2025-09-01 07:24:12.564137+00	2025-09-01 14:01:03.466415+00	\N
331112fd-deb3-4942-b909-7417d7527bfd	9d2505ce-b469-4345-a7c9-e9e425c941b1	3	2	http://localhost:9000/repair-file/2025/09/01/c79b2b41-36ef-42bc-b05d-3a0c23545a28_20250901_152446.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123123123123	\N	防守打法山东人方式	\N	\N	方法	\N	\N	2025-09-01 07:24:46.193532+00	2025-09-01 14:01:03.466415+00	\N
f010f658-cad8-4cf7-8be2-2e477ee60649	9d2505ce-b469-4345-a7c9-e9e425c941b1	4	2	http://localhost:9000/repair-file/2025/09/01/f283f3d2-cb7d-4ab9-aeba-e9841ee63166_20250901_152412.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	各位电饭锅所发生的防守打法	\N	12333	\N	\N	11132312	\N	8d31fa92-a873-46ac-9812-ece9b0c7f1cf	2025-09-01 07:25:02.79773+00	2025-09-01 14:01:03.466415+00	\N
0b72c7cc-77e2-42cd-9834-deac0af5b9e5	9d2505ce-b469-4345-a7c9-e9e425c941b1	5	1	http://localhost:9000/repair-file/2025/09/03/33e7d9bb-1365-4cee-b4e4-6f9a1c2a2bdd_20250903_231246.png	{"size": 2345822, "filename": "login-background.png", "content_type": "image/png"}	123123	\N	12323333	\N	\N	33311	\N	\N	2025-09-03 15:12:46.210096+00	2025-09-03 15:12:46.210096+00	\N
8d93d8aa-9606-4cb4-a896-397d1d634d37	f808a8fb-7f1b-43f3-a852-df13a2a63704	1	1	http://localhost:9000/repair-file/2025/09/03/57affa6a-a25d-46c1-8a0b-342e1770fac5_20250903_231324.png	{"size": 2345822, "filename": "login-background.png", "content_type": "image/png"}	1113	http://localhost:9000/repair-file/2025/09/03/3312bd5d-9de2-470e-8d69-32eccb7828aa_20250903_231324.txt	3333	\N	\N	1111	\N	\N	2025-09-03 15:13:24.669232+00	2025-09-03 15:13:24.669232+00	\N
47161f0d-c90c-4933-bcfa-d0bbc45dd760	f808a8fb-7f1b-43f3-a852-df13a2a63704	2	1	http://localhost:9000/repair-file/2025/09/03/a862f5a7-6c6c-4f0c-9770-fb75acd5ab00_20250903_231356.png	{"size": 2345822, "filename": "login-background.png", "content_type": "image/png"}	3331	http://localhost:9000/repair-file/2025/09/03/4ac82aa1-c271-410f-8d76-daa16edcc4e5_20250903_231357.txt	3333dasdasdasdssd	\N	\N	dasddasdadsas	\N	\N	2025-09-03 15:13:56.965901+00	2025-09-03 15:13:56.965901+00	\N
bd3ab44f-e78f-4003-b4a7-b73812f8f06d	9d2505ce-b469-4345-a7c9-e9e425c941b1	6	2	http://localhost:9000/repair-file/2025/09/01/f283f3d2-cb7d-4ab9-aeba-e9841ee63166_20250901_152412.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	各位电饭锅所发生的防守打法	\N	12333	\N	\N	11132312	\N	8d31fa92-a873-46ac-9812-ece9b0c7f1cf	2025-09-03 15:40:52.441195+00	2025-09-03 15:40:52.441195+00	\N
505bdeb4-72f6-4572-b575-8de5790be44d	9d2505ce-b469-4345-a7c9-e9e425c941b1	7	1	http://localhost:9000/repair-file/2025/09/07/cbe8fbfb-e1f7-49ca-a6a0-5a3d1bec465b_20250907_223923.png	{"size": 5222900, "filename": "登录.png", "content_type": "image/png"}	\N	\N	\N	\N	\N	\N	\N	\N	2025-09-07 14:39:23.189045+00	2025-09-07 14:39:23.189045+00	\N
dd3cd7c5-be74-40fe-a4c2-a81bc8e6a8d4	9d2505ce-b469-4345-a7c9-e9e425c941b1	8	1	http://localhost:9000/repair-file/2025/09/07/f0ea163d-d00f-4dc6-8fce-81c920a9b6c0_20250907_224707.png	{"size": 78453, "filename": "1.png", "content_type": "image/png"}	\N	\N	\N	\N	\N	\N	\N	\N	2025-09-07 14:47:07.574906+00	2025-09-07 14:47:07.574906+00	\N
41fdf2e6-ac3c-40e2-9ddc-fff3cbfa55dd	38a7f60e-53c6-4db8-a036-486bbcb977ae	1	1	http://localhost:9000/repair-file/2025/09/07/96922115-635d-4412-80fb-efa7b5178158_20250907_224833.png	{"size": 201296, "filename": "修复管理.png", "content_type": "image/png"}	\N	\N	\N	\N	\N	\N	\N	\N	2025-09-07 14:48:33.566054+00	2025-09-07 14:48:33.566054+00	\N
18e8c1fa-64e7-449c-bdcc-1c267b99a3a8	38a7f60e-53c6-4db8-a036-486bbcb977ae	2	1	http://localhost:9000/repair-file/2025/09/07/1ffa7405-c93f-4771-ac61-9f842f7e8505_20250907_224904.png	{"size": 5222900, "filename": "登录.png", "content_type": "image/png"}	\N	\N	\N	\N	\N	\N	\N	\N	2025-09-07 14:49:04.470559+00	2025-09-07 14:49:04.470559+00	\N
df7ad321-aa07-41d7-9902-a41f3a74ad8d	38a7f60e-53c6-4db8-a036-486bbcb977ae	3	1	\N	null	\N	\N	\N	\N	\N	\N	\N	\N	2025-09-07 15:23:08.918806+00	2025-09-07 15:23:08.918806+00	\N
16fe6c4f-eae9-41cb-865d-ac687e770485	38a7f60e-53c6-4db8-a036-486bbcb977ae	4	1	\N	null	erwere	\N	qwee	\N	\N	qwqeqeq	\N	\N	2025-09-07 15:23:29.580497+00	2025-09-07 15:23:29.580497+00	\N
7752b523-14db-4fd2-8e54-27f2b63e02e7	6745b1de-79ad-4468-8fa9-6c23bb8330db	1	1	\N	null	eqwe	\N	\N	\N	\N	\N	\N	\N	2025-09-07 15:58:25.667069+00	2025-09-07 15:58:25.667069+00	\N
3d8007cb-0b01-4f64-8d6e-152b42cf1429	6745b1de-79ad-4468-8fa9-6c23bb8330db	2	1	http://localhost:9000/repair-file/2025/09/08/ae62eff8-19c0-4f48-921f-02d3d33e2f0e_20250908_000129.png	{"size": 744416, "filename": "edited_image.png", "content_type": "image/png"}	eqwe	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:01:29.866477+00	2025-09-07 16:01:29.866477+00	\N
ad86bd34-af64-4d2a-b5b2-928fdbfe90eb	f4e4032c-bd7f-4345-b455-082963339c74	2	1	http://localhost:9000/repair-file/2025/09/08/060a68d8-ad78-4c90-8f4d-c59ff821f673_20250908_001938.png	{"size": 70875, "filename": "edited_image.png", "content_type": "image/png"}	123123	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:19:38.36715+00	2025-09-07 16:19:38.36715+00	\N
9ed83428-a405-4bb2-b45f-ba8c5df8fc7e	f4e4032c-bd7f-4345-b455-082963339c74	10	1	http://localhost:9000/repair-file/2025/09/08/2a2aa56f-252a-4c71-95d1-f1a152dc7045_20250908_010622.png	{"size": 20615, "filename": "edited_image.png", "content_type": "image/png"}	33123	\N	\N	\N	\N	\N	\N	\N	2025-09-07 17:06:22.220665+00	2025-09-07 17:06:22.220665+00	\N
2db04417-36b7-4a61-ace0-7772dd4f8885	f4e4032c-bd7f-4345-b455-082963339c74	11	1	http://localhost:9000/repair-file/2025/09/08/ea2a916c-820b-4583-81a8-809cf6f3db7e_20250908_012733.png	{"size": 34668, "filename": "edited_image.png", "content_type": "image/png"}	3123213	\N	\N	\N	\N	\N	\N	\N	2025-09-07 17:27:33.499785+00	2025-09-07 17:27:33.499785+00	\N
60b41b16-0afe-402f-9f50-06291745199c	6745b1de-79ad-4468-8fa9-6c23bb8330db	3	1	http://localhost:9000/repair-file/2025/09/08/e515971a-6624-48cd-8b7b-ce974198a9e6_20250908_000458.png	{"size": 744416, "filename": "edited_image.png", "content_type": "image/png"}	eqwe	\N	rr3erwerewr 	\N	\N	werwererwreerwrwe	\N	\N	2025-09-07 16:04:58.921454+00	2025-09-07 16:04:58.921454+00	\N
be6bf62f-36fd-476e-a0bd-9b66454e6093	9d2505ce-b469-4345-a7c9-e9e425c941b1	9	1	http://localhost:9000/repair-file/2025/09/08/224d9e93-f024-43c4-9161-26f423dfc901_20250908_000920.png	{"size": 51785, "filename": "edited_image.png", "content_type": "image/png"}	3333	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:09:20.444178+00	2025-09-07 16:09:20.444178+00	\N
b281865a-4933-4bdb-87f0-7616c9bb610f	f4e4032c-bd7f-4345-b455-082963339c74	4	1	http://localhost:9000/repair-file/2025/09/08/970a0d6e-eea0-4102-b01e-756ccc759143_20250908_003616.png	{"size": 49305, "filename": "edited_image.png", "content_type": "image/png"}	33	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:36:16.979342+00	2025-09-07 16:36:16.979342+00	\N
95c64cb3-6c24-4c21-a561-a6f254814251	f4e4032c-bd7f-4345-b455-082963339c74	6	1	http://localhost:9000/repair-file/2025/09/08/09bbb8f1-f3b8-45be-b235-25285d26d8e9_20250908_004430.png	{"size": 744671, "filename": "edited_image.png", "content_type": "image/png"}	555665	http://localhost:9000/repair-file/2025/09/08/205f7f71-e477-4459-b56c-145ce7843dad_20250908_004430.txt	1232312312312	\N	http://localhost:9000/repair-file/2025/09/08/112eb0e9-e2b7-4755-a6d7-dcaf1fbea3f2_20250908_004430.txt	3123123fasdasdad	http://localhost:9000/repair-file/2025/09/08/0fceb7b8-c57d-4900-a11d-f60bcc673665_20250908_004430.py	\N	2025-09-07 16:44:30.022609+00	2025-09-07 16:44:30.022609+00	\N
3bc4222f-2a4c-438b-ae65-c649791d089f	f4e4032c-bd7f-4345-b455-082963339c74	9	1	http://localhost:9000/repair-file/2025/09/08/2f04a71a-0c34-4820-b015-85110c4432d2_20250908_004825.png	{"size": 48479, "filename": "edited_image.png", "content_type": "image/png"}	31233123	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:48:25.063184+00	2025-09-07 16:48:25.063184+00	\N
65253572-5b1d-4321-929c-689b89c7c54c	6745b1de-79ad-4468-8fa9-6c23bb8330db	4	1	http://localhost:9000/repair-file/2025/09/08/fbcd7d68-d85e-4dac-a15a-44c7f99b272f_20250908_000636.png	{"size": 747821, "filename": "edited_image.png", "content_type": "image/png"}	eqwe	\N	rr3erwerewr 	\N	\N	werwererwreerwrwe	\N	\N	2025-09-07 16:06:36.070248+00	2025-09-07 16:06:36.070248+00	\N
f611fd48-975d-4698-9481-0e82a5276e6e	9d2505ce-b469-4345-a7c9-e9e425c941b1	10	1	http://localhost:9000/repair-file/2025/09/08/f13c0635-58e1-4fc2-aa26-1a8c8b6c52cf_20250908_001201.png	{"size": 742659, "filename": "edited_image.png", "content_type": "image/png"}	3333	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:12:01.843532+00	2025-09-07 16:12:01.843532+00	\N
cb80bd3d-0db3-4dfb-b446-ec6254fdf10f	6745b1de-79ad-4468-8fa9-6c23bb8330db	5	1	http://localhost:9000/repair-file/2025/09/08/5471c5bf-9a5a-49bf-9b5e-d6ccc01d0224_20250908_001252.png	{"size": 747821, "filename": "edited_image.png", "content_type": "image/png"}	eqwe	http://localhost:9000/repair-file/2025/09/08/004e435b-928a-4daa-b62d-f2c710520f9c_20250908_001252.txt	rr3erwerewr 	\N	\N	werwererwreerwrwe	\N	\N	2025-09-07 16:12:52.650828+00	2025-09-07 16:12:52.650828+00	\N
63b20376-587a-4d2c-a297-38d2950c8386	f4e4032c-bd7f-4345-b455-082963339c74	1	1	http://localhost:9000/repair-file/2025/09/08/0b9b2e8b-c4a4-469a-b3b8-e60d8b5c8b04_20250908_001701.png	{"size": 51615, "filename": "edited_image.png", "content_type": "image/png"}	123	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:17:01.33612+00	2025-09-07 16:17:01.33612+00	\N
b614fc39-6bcf-4a2f-bf4b-7b580ac17520	f4e4032c-bd7f-4345-b455-082963339c74	5	1	http://localhost:9000/repair-file/2025/09/08/a37cfe2c-b290-4d65-b6df-014077dcfc29_20250908_004223.png	{"size": 743473, "filename": "edited_image.png", "content_type": "image/png"}	444	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:42:23.686857+00	2025-09-07 16:42:23.686857+00	\N
2edb023f-1c74-43e8-809f-ac605049da4f	f4e4032c-bd7f-4345-b455-082963339c74	7	1	http://localhost:9000/repair-file/2025/09/08/58b57f37-25bd-4861-a978-11eaa98d905d_20250908_004507.png	{"size": 48479, "filename": "edited_image.png", "content_type": "image/png"}	33333333	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:45:07.262293+00	2025-09-07 16:45:07.262293+00	\N
2e204b72-5d32-41ee-a5f2-6cd4487c5e47	f4e4032c-bd7f-4345-b455-082963339c74	8	1	http://localhost:9000/repair-file/2025/09/08/c1d08119-796a-47a7-91a8-79d23c1a8b21_20250908_004615.png	{"size": 51409, "filename": "edited_image.png", "content_type": "image/png"}	2133123	\N	312312123	\N	\N	132321312	\N	\N	2025-09-07 16:46:15.702002+00	2025-09-07 16:46:15.702002+00	\N
4d5dd0a6-076a-4da8-8f97-a9e0ee0d7f71	f4e4032c-bd7f-4345-b455-082963339c74	3	1	http://localhost:9000/repair-file/2025/09/08/a745a584-3dc9-4ac8-affb-ad9ffecac15d_20250908_002027.png	{"size": 74282, "filename": "edited_image.png", "content_type": "image/png"}	123213	\N	\N	\N	\N	\N	\N	\N	2025-09-07 16:20:27.346359+00	2025-09-07 16:20:27.346359+00	\N
0923c975-8575-4dd8-a66e-6d2ee8993d91	f4e4032c-bd7f-4345-b455-082963339c74	12	1	http://localhost:9000/repair-file/2025/09/08/81aff4bd-8cb8-4a81-b399-3dc2a20d5fe9_20250908_120206.png	{"size": 51564, "filename": "edited_image.png", "content_type": "image/png"}	21	\N	\N	\N	\N	\N	\N	\N	2025-09-08 04:02:06.665306+00	2025-09-08 04:02:06.665306+00	\N
14dd7c01-827e-437b-9c8e-fa9aac8aa48a	f808a8fb-7f1b-43f3-a852-df13a2a63704	3	1	http://localhost:9000/repair-file/2025/09/08/8e2ee2bf-dc97-41d5-93f1-7f038d34623e_20250908_123003.png	{"size": 89842, "filename": "edited_image.png", "content_type": "image/png"}	55	\N	\N	\N	\N	\N	\N	\N	2025-09-08 04:30:03.279543+00	2025-09-08 04:30:03.279543+00	\N
204b426b-f336-4299-830d-5575d8ab07ad	38a7f60e-53c6-4db8-a036-486bbcb977ae	5	1	http://localhost:9000/repair-file/2025/09/08/9e71a2ac-a8b5-4a6b-95e0-efee6f97ea39_20250908_135306.png	{"size": 746396, "filename": "edited_image.png", "content_type": "image/png"}	58725725	\N	\N	\N	\N	\N	\N	\N	2025-09-08 05:53:06.474708+00	2025-09-08 05:53:06.474708+00	\N
ba408fe8-fdc9-4c4a-a174-9843e2d455a0	38a7f60e-53c6-4db8-a036-486bbcb977ae	6	1	http://localhost:9000/repair-file/2025/09/08/ca0f43f0-bc77-40f8-9f04-89d411d5cd51_20250908_142411.png	{"size": 51054, "filename": "edited_image.png", "content_type": "image/png"}	123312	\N	\N	\N	\N	\N	\N	\N	2025-09-08 06:24:11.647602+00	2025-09-08 06:24:11.647602+00	\N
ce321c0a-0c69-484b-a736-c43c18e4a63b	f808a8fb-7f1b-43f3-a852-df13a2a63704	4	1	http://localhost:9000/repair-file/2025/09/08/0c5cabda-e40c-44a8-a4c4-9870bd7ffd65_20250908_145022.png	{"size": 746287, "filename": "edited_image.png", "content_type": "image/png"}	123	\N	\N	\N	\N	\N	\N	\N	2025-09-08 06:50:22.906986+00	2025-09-08 06:50:22.906986+00	\N
acc6797f-e555-41fb-8022-0cc806548a5e	f808a8fb-7f1b-43f3-a852-df13a2a63704	5	1	http://localhost:9000/repair-file/2025/09/08/1a061908-953c-4883-a491-4e748a86cc47_20250908_150418.png	{"size": 747328, "filename": "edited_image.png", "content_type": "image/png"}	12321312	http://localhost:9000/repair-file/2025/09/08/0a7e2043-5a33-4f7c-9f54-75034ba0a186_20250908_150418.txt	\N	\N	http://localhost:9000/repair-file/2025/09/08/ab5b24f7-5fa1-4feb-9cc7-303769153f8e_20250908_150418.txt	\N	http://localhost:9000/repair-file/2025/09/08/20e2531a-152f-499a-b2c9-bac84e3360c3_20250908_150418.md	\N	2025-09-08 07:04:18.719615+00	2025-09-08 07:04:18.719615+00	\N
bf2c684d-6511-4b76-9beb-044e96a7dfc0	cbdc5ecd-09b5-441e-b233-5544c5af81f3	1	1	http://localhost:9000/repair-file/2025/09/08/d0537e4a-963c-4a0f-9ece-27604c59cd7b_20250908_150754.png	{"size": 748067, "filename": "edited_image.png", "content_type": "image/png"}	231313123	\N	\N	\N	\N	\N	\N	\N	2025-09-08 07:07:54.316592+00	2025-09-08 07:07:54.316592+00	\N
f0e22faf-2889-4da3-a66d-5bdafd632312	cbdc5ecd-09b5-441e-b233-5544c5af81f3	2	1	http://localhost:9000/repair-file/2025/09/08/3edc670a-767c-42c6-ac3e-ecc7b3f4e0cc_20250908_152927.png	{"size": 743597, "filename": "edited_image.png", "content_type": "image/png"}	2312312312	\N	12321312321	\N	\N	\N	\N	\N	2025-09-08 07:29:27.126947+00	2025-09-08 07:29:27.126947+00	\N
25228a17-75be-4b1e-b3be-c9cdbda6587a	cbdc5ecd-09b5-441e-b233-5544c5af81f3	3	1	http://localhost:9000/repair-file/2025/09/08/4580f1ca-116c-4c9a-9f42-780ac0497a53_20250908_155104.png	{"size": 750047, "filename": "edited_image.png", "content_type": "image/png"}	12321312323	\N	\N	\N	\N	\N	\N	\N	2025-09-08 07:51:04.223269+00	2025-09-08 07:51:04.223269+00	\N
0056b2ed-9f08-44d3-9a75-feefa43ad9f4	9d2505ce-b469-4345-a7c9-e9e425c941b1	11	2	http://localhost:9000/repair-file/2025/09/01/c79b2b41-36ef-42bc-b05d-3a0c23545a28_20250901_152446.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123123123123	\N	防守打法山东人方式	\N	\N	方法	\N	331112fd-deb3-4942-b909-7417d7527bfd	2025-09-08 08:18:02.620999+00	2025-09-08 08:18:02.620999+00	\N
69101cbc-0c26-4c79-94cd-11df9e34efa0	cbdc5ecd-09b5-441e-b233-5544c5af81f3	4	1	http://localhost:9000/repair-file/2025/09/08/8c4c4704-879c-437e-b39c-98c448a96a1a_20250908_200808.png	{"size": 1344049, "filename": "edited_image.png", "content_type": "image/png"}	这幅壁画描绘的是佛教题材的内容，展现了多位神态庄严、姿态各异的菩萨或佛弟子形象。他们或双手合十，或做其他宗教相关的手势，周围还有富有动感的装饰性线条和图案，整体营造出神圣、肃穆的宗教氛围，体现了古代佛教艺术的精湛技艺与独特审美，反映出当时的宗教文化和艺术风格。	\N	清除浮灰，清晰表达图中人物手部细节	{浮灰清理，表面处理，清晰化}	\N	\N	\N	\N	2025-09-08 12:08:08.470407+00	2025-09-08 12:08:08.470407+00	\N
aac1b750-a1b3-455d-b2d5-9af79a156bb3	cbdc5ecd-09b5-441e-b233-5544c5af81f3	5	1	http://localhost:9000/repair-file/2025/09/08/83b985a4-295a-4cc1-87b0-45a14333bffe_20250908_202626.png	{"size": 1341918, "filename": "edited_image.png", "content_type": "image/png"}	123123123	http://localhost:9000/repair-file/2025/09/08/b46f2041-5d33-46ca-a11f-6d2be116f234_20250908_202627.txt	\N	\N	http://localhost:9000/repair-file/2025/09/08/a3527a01-7fc6-4e9b-b91f-71fca98f0393_20250908_202627.txt	\N	http://localhost:9000/repair-file/2025/09/08/aeb2774a-6b88-4817-9524-17404a2ba22e_20250908_202627.txt	\N	2025-09-08 12:26:26.972524+00	2025-09-08 12:26:26.972524+00	\N
b5942903-c9b4-4ad0-bac3-8d580c68277b	10fadf91-9897-460d-ad4f-5bb38904ca25	1	1	http://localhost:9000/repair-file/2025/09/08/387def90-703e-4e5f-bdda-8ace8504e086_20250908_233610.png	{"size": 1343736, "filename": "edited_image.png", "content_type": "image/png"}	这是测试图片的	http://localhost:9000/repair-file/2025/09/08/187dc9b5-da4b-4098-983b-78a69054e608_20250908_233610.txt	测试修复意见描述	{测试,描述}	http://localhost:9000/repair-file/2025/09/08/d77a4a84-78de-4805-bf04-f36d470d9c5e_20250908_233610.txt	\N	\N	\N	2025-09-08 15:36:10.597572+00	2025-09-08 15:36:10.597572+00	\N
6bbdf9df-e5a3-4c31-a12b-7dd6146a89cd	9d2505ce-b469-4345-a7c9-e9e425c941b1	12	2	http://localhost:9000/repair-file/2025/09/01/c79b2b41-36ef-42bc-b05d-3a0c23545a28_20250901_152446.png	{"size": 1651624, "filename": "tree.png", "content_type": "image/png"}	123123123123	\N	防守打法山东人方式	\N	\N	方法	\N	331112fd-deb3-4942-b909-7417d7527bfd	2025-09-08 15:39:47.590153+00	2025-09-08 15:39:47.590153+00	\N
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (role_id, role_key, role_name) FROM stdin;
1	admin	管理员
2	restorer	修复专家
3	evaluator	评估专家
\.


--
-- Data for Name: rollback_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rollback_requests (rollback_id, workflow_id, requester_id, target_form_id, reason, status, approver_id, approved_at, created_at, support_file_url, deleted_at) FROM stdin;
3	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	8d31fa92-a873-46ac-9812-ece9b0c7f1cf	tttt	approved	1	2025-09-01 07:25:02.821298+00	2025-09-01 07:24:56.625257+00	\N	\N
1	5d952765-cce8-4cab-8db1-ffeb0096b3dd	2	17ad28e5-628d-4a3a-a9c7-db075e65c67f	333	approved	1	2025-09-01 07:20:56.184809+00	2025-09-01 07:19:28.438483+00	\N	2025-09-03 11:30:30.296883+00
5	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	8d31fa92-a873-46ac-9812-ece9b0c7f1cf	weeqw	approved	1	2025-09-03 15:40:52.499412+00	2025-09-03 15:16:36.058239+00	http://localhost:9000/repair-file/2025/09/03/eac77ff6-d857-468c-95b5-405118501daf_20250903_231636.txt	\N
7	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	331112fd-deb3-4942-b909-7417d7527bfd	31231232133123123	approved	1	2025-09-08 08:18:02.642527+00	2025-09-08 08:17:32.892974+00	http://localhost:9000/repair-file/2025/09/08/e9c32abe-d1d8-446c-8c26-c12c50bfef7c_20250908_161732.png	\N
6	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	8d31fa92-a873-46ac-9812-ece9b0c7f1cf	回溯	rejected	1	2025-09-08 08:18:05.124734+00	2025-09-08 08:14:53.901558+00	http://localhost:9000/repair-file/2025/09/08/a134c3fc-1dce-445e-aae9-3ba549a44e49_20250908_161453.png	\N
2	5d952765-cce8-4cab-8db1-ffeb0096b3dd	2	17ad28e5-628d-4a3a-a9c7-db075e65c67f	333	approved	1	2025-09-01 07:21:48.480473+00	2025-09-01 07:21:28.553196+00	\N	2025-09-08 11:59:50.338868+00
4	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	a32e3fb0-bd5f-4e32-9174-e488d9539d01	恶趣味气味儿请求	rejected	1	2025-09-01 08:09:08.177758+00	2025-09-01 08:08:47.363846+00	\N	2025-09-08 11:59:50.338868+00
8	9d2505ce-b469-4345-a7c9-e9e425c941b1	2	331112fd-deb3-4942-b909-7417d7527bfd	申请回溯	approved	1	2025-09-08 15:39:47.618409+00	2025-09-08 15:37:58.145605+00	\N	\N
\.


--
-- Data for Name: step_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.step_logs (step_log_id, form_id, action, operator_id, comment, created_at) FROM stdin;
3	ae72b18f-49d1-4109-af5f-2fa7f2e6e935	submit	1	提交第1步修复表单	2025-09-01 06:58:13.837403+00
4	b3973eb7-d406-44ac-b754-a9812308d2f9	submit	2	提交第1步修复表单	2025-09-01 06:59:21.565943+00
5	b3973eb7-d406-44ac-b754-a9812308d2f9	finalize	1	设置为最终方案	2025-09-01 07:00:36.519551+00
6	40f34d5d-7710-4322-a9d4-0fcfc6d9b3f6	submit	1	提交第2步修复表单	2025-09-01 07:01:10.479848+00
7	dd434189-4bf6-48f8-b0b3-b10aed2a613e	submit	1	提交第3步修复表单	2025-09-01 07:01:27.996332+00
8	17ad28e5-628d-4a3a-a9c7-db075e65c67f	submit	2	提交第1步修复表单	2025-09-01 07:07:39.265854+00
9	ea83f02f-d94d-487f-800d-d8b4d5237399	submit	2	提交第2步修复表单	2025-09-01 07:19:20.525108+00
12	59f085e1-0e1a-4e68-a14d-94634b72a64a	rollback	1	回溯到表单17ad28e5-628d-4a3a-a9c7-db075e65c67f	2025-09-01 07:20:56.184809+00
13	37b79bae-3876-464b-b6d7-bd622735ab2f	rollback	1	回溯到表单17ad28e5-628d-4a3a-a9c7-db075e65c67f	2025-09-01 07:21:48.480473+00
14	ea83f02f-d94d-487f-800d-d8b4d5237399	finalize	2	设置为最终方案	2025-09-01 07:23:15.951662+00
15	a32e3fb0-bd5f-4e32-9174-e488d9539d01	submit	2	提交第1步修复表单	2025-09-01 07:23:57.862324+00
16	8d31fa92-a873-46ac-9812-ece9b0c7f1cf	submit	2	提交第2步修复表单	2025-09-01 07:24:12.600586+00
17	331112fd-deb3-4942-b909-7417d7527bfd	submit	2	提交第3步修复表单	2025-09-01 07:24:46.265157+00
18	f010f658-cad8-4cf7-8be2-2e477ee60649	rollback	1	回溯到表单8d31fa92-a873-46ac-9812-ece9b0c7f1cf	2025-09-01 07:25:02.821298+00
19	0b72c7cc-77e2-42cd-9834-deac0af5b9e5	submit	1	提交第5步修复表单	2025-09-03 15:12:46.305056+00
20	8d93d8aa-9606-4cb4-a896-397d1d634d37	submit	1	提交第1步修复表单	2025-09-03 15:13:24.772482+00
21	47161f0d-c90c-4933-bcfa-d0bbc45dd760	submit	1	提交第2步修复表单	2025-09-03 15:13:57.077574+00
22	dd434189-4bf6-48f8-b0b3-b10aed2a613e	finalize	1	设置为最终方案	2025-09-03 15:15:14.248519+00
23	bd3ab44f-e78f-4003-b4a7-b73812f8f06d	rollback	1	回溯到表单8d31fa92-a873-46ac-9812-ece9b0c7f1cf	2025-09-03 15:40:52.499412+00
24	505bdeb4-72f6-4572-b575-8de5790be44d	submit	1	提交第7步修复表单	2025-09-07 14:39:23.296143+00
25	dd3cd7c5-be74-40fe-a4c2-a81bc8e6a8d4	submit	1	提交第8步修复表单	2025-09-07 14:47:07.60392+00
26	41fdf2e6-ac3c-40e2-9ddc-fff3cbfa55dd	submit	1	提交第1步修复表单	2025-09-07 14:48:33.631224+00
27	18e8c1fa-64e7-449c-bdcc-1c267b99a3a8	submit	1	提交第2步修复表单	2025-09-07 14:49:04.515095+00
28	df7ad321-aa07-41d7-9902-a41f3a74ad8d	submit	1	提交第3步修复表单	2025-09-07 15:23:08.939309+00
29	16fe6c4f-eae9-41cb-865d-ac687e770485	submit	1	提交第4步修复表单	2025-09-07 15:23:29.596753+00
30	7752b523-14db-4fd2-8e54-27f2b63e02e7	submit	1	提交第1步修复表单	2025-09-07 15:58:25.679612+00
31	3d8007cb-0b01-4f64-8d6e-152b42cf1429	submit	1	提交第2步修复表单	2025-09-07 16:01:29.910367+00
32	60b41b16-0afe-402f-9f50-06291745199c	submit	1	提交第3步修复表单	2025-09-07 16:04:58.961552+00
33	65253572-5b1d-4321-929c-689b89c7c54c	submit	1	提交第4步修复表单	2025-09-07 16:06:36.10032+00
34	be6bf62f-36fd-476e-a0bd-9b66454e6093	submit	1	提交第9步修复表单	2025-09-07 16:09:20.467614+00
35	f611fd48-975d-4698-9481-0e82a5276e6e	submit	1	提交第10步修复表单	2025-09-07 16:12:01.875445+00
36	cb80bd3d-0db3-4dfb-b446-ec6254fdf10f	submit	1	提交第5步修复表单	2025-09-07 16:12:52.723617+00
37	3d8007cb-0b01-4f64-8d6e-152b42cf1429	finalize	1	设置为最终方案	2025-09-07 16:15:50.792675+00
38	63b20376-587a-4d2c-a297-38d2950c8386	submit	1	提交第1步修复表单	2025-09-07 16:17:01.359873+00
39	ad86bd34-af64-4d2a-b5b2-928fdbfe90eb	submit	1	提交第2步修复表单	2025-09-07 16:19:38.391849+00
40	4d5dd0a6-076a-4da8-8f97-a9e0ee0d7f71	submit	1	提交第3步修复表单	2025-09-07 16:20:27.369592+00
41	b281865a-4933-4bdb-87f0-7616c9bb610f	submit	1	提交第4步修复表单	2025-09-07 16:36:17.034543+00
42	b614fc39-6bcf-4a2f-bf4b-7b580ac17520	submit	1	提交第5步修复表单	2025-09-07 16:42:23.716035+00
43	95c64cb3-6c24-4c21-a561-a6f254814251	submit	1	提交第6步修复表单	2025-09-07 16:44:30.234538+00
44	2edb023f-1c74-43e8-809f-ac605049da4f	submit	1	提交第7步修复表单	2025-09-07 16:45:07.282454+00
45	2e204b72-5d32-41ee-a5f2-6cd4487c5e47	submit	1	提交第8步修复表单	2025-09-07 16:46:15.721187+00
46	3bc4222f-2a4c-438b-ae65-c649791d089f	submit	1	提交第9步修复表单	2025-09-07 16:48:25.08143+00
47	9ed83428-a405-4bb2-b45f-ba8c5df8fc7e	submit	1	提交第10步修复表单	2025-09-07 17:06:22.23959+00
48	2db04417-36b7-4a61-ace0-7772dd4f8885	submit	1	提交第11步修复表单	2025-09-07 17:27:33.524718+00
49	0923c975-8575-4dd8-a66e-6d2ee8993d91	submit	1	提交第12步修复表单	2025-09-08 04:02:06.698592+00
50	ad86bd34-af64-4d2a-b5b2-928fdbfe90eb	finalize	1	设置为最终方案	2025-09-08 04:02:46.441337+00
51	14dd7c01-827e-437b-9c8e-fa9aac8aa48a	submit	1	提交第3步修复表单	2025-09-08 04:30:03.303872+00
52	204b426b-f336-4299-830d-5575d8ab07ad	submit	1	提交第5步修复表单	2025-09-08 05:53:06.522783+00
53	ba408fe8-fdc9-4c4a-a174-9843e2d455a0	submit	1	提交第6步修复表单	2025-09-08 06:24:11.673741+00
54	ce321c0a-0c69-484b-a736-c43c18e4a63b	submit	1	提交第4步修复表单	2025-09-08 06:50:22.946059+00
55	acc6797f-e555-41fb-8022-0cc806548a5e	submit	1	提交第5步修复表单	2025-09-08 07:04:18.891948+00
56	bf2c684d-6511-4b76-9beb-044e96a7dfc0	submit	1	提交第1步修复表单	2025-09-08 07:07:54.367688+00
57	f0e22faf-2889-4da3-a66d-5bdafd632312	submit	1	提交第2步修复表单	2025-09-08 07:29:27.203134+00
58	25228a17-75be-4b1e-b3be-c9cdbda6587a	submit	1	提交第3步修复表单	2025-09-08 07:51:04.264029+00
59	0056b2ed-9f08-44d3-9a75-feefa43ad9f4	rollback	1	回溯到表单331112fd-deb3-4942-b909-7417d7527bfd	2025-09-08 08:18:02.642527+00
60	69101cbc-0c26-4c79-94cd-11df9e34efa0	submit	1	提交第4步修复表单	2025-09-08 12:08:08.512755+00
61	aac1b750-a1b3-455d-b2d5-9af79a156bb3	submit	1	提交第5步修复表单	2025-09-08 12:26:27.156604+00
62	b5942903-c9b4-4ad0-bac3-8d580c68277b	submit	1	提交第1步修复表单	2025-09-08 15:36:10.646222+00
63	6bbdf9df-e5a3-4c31-a12b-7dd6146a89cd	rollback	1	回溯到表单331112fd-deb3-4942-b909-7417d7527bfd	2025-09-08 15:39:47.618409+00
\.


--
-- Data for Name: system_configs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_configs (config_key, config_value, description, updated_at) FROM stdin;
privacy_agreement	保密协议\n\n尊敬的用户：\n\n感谢您使用克孜尔石窟壁画智慧修复全生命周期管理系统。为了保护珍贵的文物信息和相关技术资料，请您仔细阅读并同意以下保密条款：\n\n1. 保密义务\n   您承诺对在使用本系统过程中接触到的所有壁画图像、修复技术、工艺流程等信息严格保密。\n\n2. 信息安全\n   未经授权，不得复制、传播、泄露任何系统中的文物信息。\n\n3. 使用限制\n   仅可将获得的信息用于指定的修复工作，不得用于其他商业或个人目的。\n\n4. 责任承担\n   如违反保密义务造成损失，将承担相应的法律责任。\n\n请仔细阅读上述条款，点击"同意"按钮表示您已完全理解并同意遵守本保密协议。	用户保密协议内容	2025-09-01 06:47:56.119172+00
workflow_status_options	draft,in_progress,completed,cancelled	工作流状态选项	2025-09-01 13:25:01.251775+00
rollback_status_options	pending,approved,rejected	回退请求状态选项	2025-09-01 13:25:01.251775+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, username, password_hash, full_name, role_id, email, phone, is_active, created_at, updated_at, deleted_at) FROM stdin;
2	restorer1	$2b$12$2/Dcdje9VD402vOF7ejX9uNu8/hv/qCkaw9HPk/eyvn5iGxTczo/q	修复专家张三	2	restorer1@repair.com	\N	t	2025-09-01 06:47:56.119172+00	2025-09-01 06:47:56.119172+00	\N
3	evaluator1	$2b$12$zLd.ZvVh89oO/dOcR.zysOpXk9LrP5VgIvMhZ67gNCYFPImL6Tbja	评估专家李四	3	evaluator1@repair.com	\N	t	2025-09-01 06:47:56.119172+00	2025-09-01 06:47:56.119172+00	\N
4	restorer	$2b$12$teDkzrT0uHS8sPf9RyK9SODmKf/v.WzHMlA/XMugsNwzlFnlTGqS.	修复专家	2	restorer@example.com	\N	t	2025-09-01 13:25:01.251775+00	2025-09-01 13:25:01.251775+00	\N
5	evaluator	$2b$12$K4poDYCfbD9eMKZxWOH4P.egverWHUIZDD6.Xbw/wjhPp5AstHvOu	评估专家	3	evaluator@example.com	\N	t	2025-09-01 13:25:01.251775+00	2025-09-01 13:25:01.251775+00	\N
1	admin	$2b$12$2EOIMht.oQVqEGR79GwgSu4XPPyvQgeLYR1Q9tdHueLOtG2Th2lVm	系统管理员	1	admin@repair.com	13446589745	t	2025-09-01 06:47:56.119172+00	2025-09-03 10:34:12.943839+00	\N
\.


--
-- Data for Name: workflows; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflows (workflow_id, title, description, initiator_id, current_step, status, is_finalized, created_at, updated_at, deleted_at) FROM stdin;
f808a8fb-7f1b-43f3-a852-df13a2a63704	cese	cese	1	5	running	f	2025-09-03 15:04:19.022814+00	2025-09-08 07:04:18.719615+00	\N
51c9844a-9bf5-4c6e-ba1b-4a060cbaa361	90	09	1	1	finished	f	2025-09-03 12:59:57.065079+00	2025-09-08 11:25:50.656195+00	2025-09-08 11:25:50.656195
47b650e5-233f-49ef-ae20-48706e5aeead	ces	ces	1	1	finished	f	2025-09-03 12:48:19.287342+00	2025-09-08 11:25:53.93132+00	2025-09-08 11:25:53.93132
90b489ba-912f-42e0-a257-e364ebd2e131	测试	这是测试	1	1	finished	f	2025-09-01 15:10:22.143965+00	2025-09-08 11:25:58.020759+00	2025-09-08 11:25:58.020759
5d952765-cce8-4cab-8db1-ffeb0096b3dd	232123	3333	2	4	finished	t	2025-09-01 07:07:19.191218+00	2025-09-08 11:26:01.83695+00	2025-09-08 11:26:01.83695
161251f8-2c78-4220-ab36-bc8622bb71a8	123213	1321312321	2	1	finished	t	2025-09-01 06:59:10.865955+00	2025-09-08 11:26:03.815222+00	2025-09-08 11:26:03.815222
26f1d627-5407-4c5d-b203-74dbf745d10a	56	56	1	1	finished	f	2025-09-03 12:59:50.424826+00	2025-09-08 11:26:06.197331+00	2025-09-08 11:26:06.197331
02b13dd1-0078-40d4-b1a4-c260801ab2ac	45	54	1	1	finished	f	2025-09-03 13:00:00.732046+00	2025-09-08 11:26:08.144923+00	2025-09-08 11:26:08.144923
cbdc5ecd-09b5-441e-b233-5544c5af81f3	qqwe	weqeqeqw	1	5	running	f	2025-09-08 07:06:34.409152+00	2025-09-08 12:26:26.972524+00	\N
10fadf91-9897-460d-ad4f-5bb38904ca25	测试工作流	测试演示	1	1	running	f	2025-09-08 15:33:08.253661+00	2025-09-08 15:36:10.597572+00	\N
6745b1de-79ad-4468-8fa9-6c23bb8330db	rr	rrq	1	5	finished	t	2025-09-07 15:26:03.331014+00	2025-09-08 15:36:50.696207+00	2025-09-08 15:36:50.696207
9d2505ce-b469-4345-a7c9-e9e425c941b1	1232323123	12333333	2	12	running	f	2025-09-01 07:23:43.105174+00	2025-09-08 15:39:47.590153+00	\N
063d8e8c-d67b-4bb9-819b-b0e22b27677d	232	333	1	3	finished	t	2025-09-01 06:53:00.026364+00	2025-09-03 15:15:14.248519+00	\N
f4e4032c-bd7f-4345-b455-082963339c74	333	333	1	12	finished	t	2025-09-07 16:16:31.235708+00	2025-09-08 04:02:46.441337+00	\N
38a7f60e-53c6-4db8-a036-486bbcb977ae	rteces	getrnion	1	6	running	f	2025-09-07 14:47:53.714108+00	2025-09-08 06:24:11.647602+00	\N
\.


--
-- Name: evaluations_evaluate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.evaluations_evaluate_id_seq', 6, true);


--
-- Name: roles_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_role_id_seq', 3, true);


--
-- Name: rollback_requests_rollback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rollback_requests_rollback_id_seq', 8, true);


--
-- Name: step_logs_step_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.step_logs_step_log_id_seq', 63, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 5, true);


--
-- Name: evaluations evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_pkey PRIMARY KEY (evaluate_id);


--
-- Name: forms forms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_pkey PRIMARY KEY (form_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: roles roles_role_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_key_key UNIQUE (role_key);


--
-- Name: rollback_requests rollback_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rollback_requests
    ADD CONSTRAINT rollback_requests_pkey PRIMARY KEY (rollback_id);


--
-- Name: step_logs step_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.step_logs
    ADD CONSTRAINT step_logs_pkey PRIMARY KEY (step_log_id);


--
-- Name: system_configs system_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_configs
    ADD CONSTRAINT system_configs_pkey PRIMARY KEY (config_key);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: workflows workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_pkey PRIMARY KEY (workflow_id);


--
-- Name: evaluations evaluations_evaluator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_evaluator_id_fkey FOREIGN KEY (evaluator_id) REFERENCES public.users(user_id);


--
-- Name: evaluations evaluations_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id);


--
-- Name: forms forms_is_rollback_from_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_is_rollback_from_fkey FOREIGN KEY (is_rollback_from) REFERENCES public.forms(form_id);


--
-- Name: forms forms_submitter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_submitter_id_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(user_id);


--
-- Name: forms forms_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id);


--
-- Name: rollback_requests rollback_requests_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rollback_requests
    ADD CONSTRAINT rollback_requests_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.users(user_id);


--
-- Name: rollback_requests rollback_requests_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rollback_requests
    ADD CONSTRAINT rollback_requests_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.users(user_id);


--
-- Name: rollback_requests rollback_requests_target_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rollback_requests
    ADD CONSTRAINT rollback_requests_target_form_id_fkey FOREIGN KEY (target_form_id) REFERENCES public.forms(form_id);


--
-- Name: rollback_requests rollback_requests_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rollback_requests
    ADD CONSTRAINT rollback_requests_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(workflow_id);


--
-- Name: step_logs step_logs_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.step_logs
    ADD CONSTRAINT step_logs_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.forms(form_id);


--
-- Name: step_logs step_logs_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.step_logs
    ADD CONSTRAINT step_logs_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(role_id);


--
-- Name: workflows workflows_initiator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_initiator_id_fkey FOREIGN KEY (initiator_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 2flBCVgvb6cBFfbRZYMF1CTwiuiQBBZHkoMmai3c38qp85IQIoDMyQjqGunN8a2

