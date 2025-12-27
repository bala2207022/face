import streamlit as st
import os
from io import BytesIO
import csv
from pathlib import Path

from src import index as core

st.set_page_config(page_title="Face Attendance", layout="wide")


def get_embedding_from_bgr(img):
    """Return a normalized embedding for a BGR image using insightface if available,
    otherwise fall back to the coarse image feature."""
    try:
        import numpy as np
        if core.HAS_INSIGHTFACE:
            try:
                app = core.face_app()
                faces = app.get(img)
            except Exception:
                faces = []
            if not faces:
                return None
            f = max(faces, key=lambda z: (z.bbox[2]-z.bbox[0])*(z.bbox[3]-z.bbox[1]))
            return f.normed_embedding.astype(core.np.float32)
        else:
            return core.compute_image_feature(img)
    except Exception:
        return None


def cosine(a, b):
    a = a / (core.np.linalg.norm(a) + 1e-12)
    b = b / (core.np.linalg.norm(b) + 1e-12)
    return float(core.np.dot(a, b))

def save_uploaded_images(uploaded_files, folder: str):
    Path(folder).mkdir(parents=True, exist_ok=True)
    written = 0
    for uf in uploaded_files:
        data = uf.getbuffer()
        out_path = os.path.join(folder, f"{int(core.time.time() * 1000)}_{uf.name}")
        with open(out_path, "wb") as f:
            f.write(data)
        written += 1
    return written

def update_class_csv(class_id: int):
    # ensure Summary sheet exists and then write it to CSV (overwrite)
    core.write_summary_sheet_for_class(class_id)
    xlpath = core._class_filepath_for_id(class_id)
    if not xlpath or not os.path.exists(xlpath):
        return None
    csv_path = os.path.splitext(xlpath)[0] + ".csv"
    try:
        wb = core.load_workbook(xlpath, data_only=True)
    except Exception:
        return None
    if "Summary" not in wb.sheetnames:
        return None
    ws = wb["Summary"]
    rows = []
    for r in ws.iter_rows(values_only=True):
        rows.append(["" if v is None else v for v in r])
    # write CSV (overwrite existing file)
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        w = csv.writer(cf)
        for row in rows:
            w.writerow(row)
    return csv_path

def list_classes():
    meta = core.load_classes_meta()
    classes = meta.get("classes", {})
    items = []
    for cid, info in classes.items():
        items.append((int(cid), info.get("class_name"), info.get("professor_name"), info.get("professor_code")))
    items.sort()
    return items

def main():
    st.title("Face Attendance — Streamlit")

    menu = st.radio("Choose an action", ["Register / Create Class", "Open Class / Check-In"], index=0)

    if menu == "Register / Create Class":
        st.header("Create Class (Professor)")
        prof_col, class_col = st.columns([1, 2])
        with prof_col:
            prof_name = st.text_input("Professor name")
            prof_code = st.text_input("Professor id (used as password)")
            target_photos = st.slider("Photos to capture for professor (camera only)", 15, 17, 15)
            # camera-only session state for professor captures
            st.session_state.setdefault("prof_caps", [])
            prof_camera = st.camera_input("Capture professor photo")
            if st.button("Add capture to queue"):
                if prof_camera is None:
                    st.error("Take a photo first using the camera widget.")
                else:
                    st.session_state["prof_caps"].append(prof_camera.getbuffer())
            st.write(f"Captured: {len(st.session_state['prof_caps'])}/{target_photos}")
            if st.button("Reset captures"):
                st.session_state["prof_caps"] = []
            if len(st.session_state["prof_caps"]) >= target_photos:
                if st.button("Save professor captures to disk"):
                    if not prof_name or not prof_code:
                        st.error("Provide professor name and id first")
                    else:
                        label = f"prof_{prof_code}_{prof_name}"
                        folder = os.path.join(core.DATA_DIR, label)
                        Path(folder).mkdir(parents=True, exist_ok=True)
                        # write captures
                        for i, b in enumerate(st.session_state["prof_caps"]):
                            out_path = os.path.join(folder, f"{int(core.time.time() * 1000)}_cap_{i}.jpg")
                            with open(out_path, "wb") as f:
                                f.write(b)
                        st.success(f"Saved {len(st.session_state['prof_caps'])} photos for professor")
                        st.session_state["prof_caps"] = []

        with class_col:
            class_name = st.text_input("Class name / subject")
            if st.button("Create class now"):
                if not prof_name or not prof_code or not class_name:
                    st.error("Provide professor name, id and class name first")
                else:
                    label = f"prof_{prof_code}_{prof_name}"
                    folder = os.path.join(core.DATA_DIR, label)
                    if not os.path.isdir(folder):
                        st.error("No professor images saved. Upload or capture images first.")
                    else:
                        # run per-image embedding checks
                        embs = []
                        valid = 0
                        from pathlib import Path as _P
                        import cv2, numpy as _np
                        for p in _P(folder).glob("*"):
                            img = cv2.imread(str(p))
                            if img is None:
                                continue
                            e = get_embedding_from_bgr(img)
                            if e is not None:
                                embs.append(e)
                                valid += 1
                        if valid < max(12, int(target_photos * 0.75)):
                            st.error(f"Not enough valid face detections ({valid}). Capture clearer photos.")
                        else:
                            # pairwise similarity checks
                            sims = []
                            for i in range(len(embs)):
                                for j in range(i+1, len(embs)):
                                    sims.append(cosine(embs[i], embs[j]))
                            mean_sim = float(_np.mean(sims)) if sims else 0.0
                            std_sim = float(_np.std(sims)) if sims else 0.0
                            if mean_sim > 0.995:
                                st.error("Captured images appear identical — possible duplicate/cheat. Vary expressions/angles.")
                            elif mean_sim < 0.5:
                                st.error("Captured images look very inconsistent. Ensure images are of the same person.")
                            else:
                                cents = core.load_centroids()
                                centroid = core.compute_centroid_for_folder(folder)
                                if centroid is None:
                                    st.error("Could not compute face embedding for professor images.")
                                else:
                                    cents[label] = centroid
                                    core.save_centroids(cents)
                                    cid = core.create_class(label, prof_name, prof_code, class_name)
                                    st.success(f"Class created: {class_name} (id {cid})")

        st.markdown("---")
        st.header("Register Student to Class")
        classes = list_classes()
        if not classes:
            st.info("No classes created yet.")
        else:
            sel = st.selectbox("Choose class", [f"{c[0]}: {c[1]} (Prof: {c[2]})" for c in classes])
            sel_id = int(str(sel).split(":", 1)[0])
            student_name = st.text_input("Student name", key="sname")
            student_code = st.text_input("Student id/code", key="scode")
            # camera-only student capture
            target_photos_stu = st.slider("Photos to capture for student (camera only)", 15, 17, 15, key="tstu")
            st.session_state.setdefault("stu_caps", [])
            student_camera = st.camera_input("Capture student photo", key="student_cam")
            if st.button("Add student capture to queue"):
                if student_camera is None:
                    st.error("Capture a photo first using the camera widget")
                else:
                    st.session_state["stu_caps"].append(student_camera.getbuffer())
            st.write(f"Captured: {len(st.session_state['stu_caps'])}/{target_photos_stu}")
            if st.button("Reset student captures"):
                st.session_state["stu_caps"] = []
            if len(st.session_state["stu_caps"]) >= target_photos_stu:
                if st.button("Register student to class"):
                    if not student_name or not student_code:
                        st.error("Provide student name and code")
                    else:
                        label = f"{student_code}_{student_name}"
                        folder = os.path.join(core.DATA_DIR, label)
                        Path(folder).mkdir(parents=True, exist_ok=True)
                        for i, b in enumerate(st.session_state["stu_caps"]):
                            out_path = os.path.join(folder, f"{int(core.time.time() * 1000)}_cap_{i}.jpg")
                            with open(out_path, "wb") as f:
                                f.write(b)
                        # run embedding checks
                        embs = []
                        import cv2, numpy as _np
                        from pathlib import Path as _P
                        for p in _P(folder).glob("*"):
                            img = cv2.imread(str(p))
                            if img is None:
                                continue
                            e = get_embedding_from_bgr(img)
                            if e is not None:
                                embs.append(e)
                        if len(embs) < max(12, int(target_photos_stu * 0.75)):
                            st.error(f"Not enough valid face detections ({len(embs)}). Capture clearer photos.")
                        else:
                            sims = []
                            for i in range(len(embs)):
                                for j in range(i+1, len(embs)):
                                    sims.append(cosine(embs[i], embs[j]))
                            mean_sim = float(_np.mean(sims)) if sims else 0.0
                            if mean_sim > 0.995:
                                st.error("Captured images appear identical — possible duplicate/cheat. Vary expressions/angles.")
                            elif mean_sim < 0.5:
                                st.error("Captured images look inconsistent. Ensure images are of the same person.")
                            else:
                                cents = core.load_centroids()
                                centroid = core.compute_centroid_for_folder(folder)
                                if centroid is None:
                                    st.error("Could not compute embedding for student images")
                                else:
                                    cents[label] = centroid
                                    core.save_centroids(cents)
                                    core.upsert_student(label, student_name, student_code)
                                    # link to class workbook
                                    filepath = core._class_filepath_for_id(sel_id)
                                    if not filepath or not os.path.exists(filepath):
                                        st.error("Class workbook not found")
                                    else:
                                        wb = core.load_workbook(filepath)
                                        ws_students = wb["students"]
                                        exists = False
                                        for r in ws_students.iter_rows(min_row=2, values_only=True):
                                            if r[1] == label or r[0] == core.get_student_id_by_face_label(label):
                                                exists = True
                                                break
                                        if not exists:
                                            ws_students.append([core.get_student_id_by_face_label(label), label, student_name, student_code, 0])
                                            wb.save(filepath)
                                        st.success(f"Student {student_name} registered to class {sel_id}")
                                    st.session_state["stu_caps"] = []

    else:
        st.header("Open Class and Check-In")
        classes = list_classes()
        if not classes:
            st.info("No classes available. Create one first.")
            return
        sel = st.selectbox("Select class to open/check", [f"{c[0]}: {c[1]} (Prof: {c[2]})" for c in classes])
        sel_id = int(str(sel).split(":", 1)[0])
        prof_login = st.text_input("Professor id (to open class)")
        if st.button("Open class (login)"):
            # verify professor code
            meta = core.load_classes_meta()
            cls = meta.get("classes", {}).get(str(sel_id))
            if not cls:
                st.error("Class metadata missing")
            elif str(cls.get("professor_code")) != str(prof_login):
                st.error("Invalid professor id/password")
            else:
                cls["session_count"] = int(cls.get("session_count", 0)) + 1
                session_id = cls["session_count"]
                core.save_classes_meta(meta)
                # append session row
                filepath = cls.get("file")
                if filepath and os.path.exists(filepath):
                    wb = core.load_workbook(filepath)
                    ws_sessions = wb["sessions"]
                    ws_sessions.append([session_id, core.datetime.now().isoformat(), "", "", "", ""])
                    wb.save(filepath)
                st.success(f"Class opened (session {session_id}). Students can now check-in.")

        st.markdown("---")
        st.subheader("Student Check-In (camera only)")
        check_camera = st.camera_input("Capture student photo for check-in")

        if st.button("Check-In Student"):
            # obtain image bytes from selected mode
            img = None
            import cv2
            import numpy as np
            if check_camera is None:
                st.error("Capture a photo first using the camera widget")
                img = None
            else:
                img_bytes = check_camera.getbuffer()
                arr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            if img is None:
                pass
            else:
                if img is None:
                    st.error("Could not read image")
                else:
                    cents = core.load_centroids()
                    if not cents:
                        st.error("No trained centroids available")
                    else:
                        # compute embedding
                        if core.HAS_INSIGHTFACE:
                            try:
                                appface = core.face_app()
                                faces = appface.get(img)
                            except Exception:
                                faces = []
                            if not faces:
                                st.info("No face detected")
                            else:
                                f = max(faces, key=lambda z: (z.bbox[2]-z.bbox[0])*(z.bbox[3]-z.bbox[1]))
                                emb = f.normed_embedding.astype(core.np.float32)
                        else:
                            emb = core.compute_image_feature(img)
                        if emb is None:
                            st.error("Could not compute embedding")
                        else:
                            best_lab, best_sim = "Unknown", -1.0
                            for lab, c in cents.items():
                                s = core.norm_cos(emb, c)
                                if s > best_sim:
                                    best_sim, best_lab = s, lab
                            if best_sim < core.THRESHOLD:
                                st.info(f"Not registered (sim={best_sim:.2f})")
                            elif best_lab.startswith("prof_"):
                                st.info("Professor detected — not a student check-in")
                            else:
                                # mark attendance
                                res = core.mark_student_attendance(best_lab, sel_id)
                                # mark_student_attendance returns (class_name, student_name, student_code, recorded_bool)
                                if len(res) >= 4:
                                    class_name, student_name, student_code, recorded = res
                                    if recorded:
                                        st.success(f"{student_name} ({student_code}) marked present for {class_name}")
                                    else:
                                        st.info(f"{student_name} ({student_code}) already marked today for {class_name}")
                                else:
                                    st.info(res)
                                # update csv for class
                                csvp = update_class_csv(sel_id)
                                if csvp:
                                    with open(csvp, "rb") as f:
                                        st.download_button("Download updated CSV", f, file_name=os.path.basename(csvp), mime="text/csv")

        st.markdown("---")
        st.subheader("Download Class CSV")
        if st.button("Prepare CSV and Show download"):
            csvp = update_class_csv(sel_id)
            if not csvp:
                st.error("Could not prepare CSV")
            else:
                with open(csvp, "rb") as f:
                    st.download_button("Download CSV", f, file_name=os.path.basename(csvp), mime="text/csv")

if __name__ == "__main__":
    main()
