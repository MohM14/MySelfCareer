import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("توليد الجدول الدراسي لطلاب برنامج نظم المعلومات الصحية")

st.markdown("""
هذا التطبيق يقوم بإنشاء جدول دراسي لكل طالب للفصل القادم مع مراعاة المتطلب السابق لكل مقرر 
(يجب أن يكون الطالب قد اجتازه سابقاً أو مسجل حالياً ويفترض نجاحه) بحيث لا يتجاوز إجمالي الساعات 20 ساعة.
""")

# رفع ملف المقررات
st.header("رفع ملف المقررات")
courses_file = st.file_uploader("اختر ملف Excel الخاص بالمقررات", type=["xlsx"], key="courses")

# رفع ملف الخطة الدراسية للطلاب
st.header("رفع ملف الخطة الدراسية للطلاب")
students_file = st.file_uploader("اختر ملف Excel الخاص بالخطة الدراسية", type=["xlsx"], key="students")

if courses_file is not None and students_file is not None:
    try:
        # قراءة ملفات الإكسل
        courses_df = pd.read_excel(courses_file)
        students_df = pd.read_excel(students_file)
        
        # تنظيف بيانات المقررات: إزالة المسافات الزائدة من رموز المقررات والمتطلبات السابقة
        courses_df['CourseCode'] = courses_df['CourseCode'].astype(str).str.strip()
        courses_df['Pre-Requisite'] = courses_df['Pre-Requisite'].astype(str).str.strip()
        
        # تنظيف أسماء أعمدة بيانات الطلاب: إزالة المسافات الزائدة
        students_df.columns = [col.strip() if isinstance(col, str) else col for col in students_df.columns]
        
        # تنظيف قيم البيانات في خلايا بيانات الطلاب (خاصةً في أعمدة المقررات)
        # حيث نقوم بتحويل كل قيمة إلى نص وإزالة المسافات الزائدة، مع المحافظة على قيم غير نصية كما هي
        def clean_value(val):
            if isinstance(val, str):
                return val.strip()
            return val
        
        students_df = students_df.applymap(clean_value)
        
        # st.subheader("بيانات المقررات")
        # st.dataframe(courses_df)
        
        # st.subheader("بيانات الخطة الدراسية")
        # st.dataframe(students_df)
        
        # تحويل عمود الساعات إلى نوع رقمي
        courses_df['Hours'] = pd.to_numeric(courses_df['Hours'], errors='coerce')
        
        # مجموعة الحالات التي تعتبر نجاح الطالب للمقرر
        passed_statuses = {'$', 'XM', 'A', '+A', 'B', '+B', 'C', '+C', '+D', 'D','P'}
        
        def generate_student_schedule(courses_df, students_df, max_hours):
            """
            تقوم الدالة بتوليد جدول دراسي لكل طالب على النحو التالي:
            - ترتيب المقررات حسب العمود "Level".
            - لكل طالب يتم المرور على المقررات التي لم يجتزها بعد (بافتراض أن الحالة "-" تعني عدم الاجتياز).
            - يتم التحقق من أن الطالب قد اجتاز المتطلب السابق (أي أن حالة المقرر الخاص بالمتطلب ضمن passed_statuses) إن وُجد.
            - تُضاف المقررات إلى جدول الطالب طالما لا يتجاوز مجموع الساعات قيمة max_hours.
            - تُحدّث الدالة ملخصاً بعدد الطلاب المحتمل لكل مقرر.
            """
            summary = {}          # لتجميع عدد الطلاب لكل مقرر
            student_schedules = {}  # لتخزين الجدول الدراسي لكل طالب
            
            # ترتيب المقررات حسب "Level"
            courses_df_sorted = courses_df.sort_values(by='Level')
            
            # المرور على كل طالب في بيانات الخطة الدراسية
            for _, student in students_df.iterrows():
                student_id = student['ID']
                total_hours = 0
                schedule = []  # قائمة المقررات المختارة للطالب
                
                # المرور على كل مقرر من ملف المقررات
                for _, course_row in courses_df_sorted.iterrows():
                    course_code = course_row['CourseCode']
                    course_hours = course_row['Hours']
                    prerequisite = course_row['Pre-Requisite']
                    
                    # التأكد من وجود عمود المقرر في بيانات الطلاب (مع مراعاة التنظيف)
                    if course_code not in students_df.columns:
                        continue
                    
                    # استرجاع حالة الطالب للمقرر وتنظيف القيمة إن كانت نصية
                    status = student[course_code]
                    if isinstance(status, str):
                        status = status.strip()
                    
                    # إذا كان الطالب قد اجتاز المقرر (وفقاً للحالات المحددة) فلا داعي لإضافته مرة أخرى
                    if status in passed_statuses:
                        continue
                    
                    # إذا كانت حالة المقرر "-" فهذا يعني أن المقرر لم يُجتز بعد.
                    # التحقق من المتطلب السابق، إذا كان موجوداً:
                    if pd.isna(prerequisite) or prerequisite == '' or prerequisite == '-' or prerequisite.lower()=='nan':
                        prereq_satisfied = True
                    else:
                        # التأكد من وجود عمود المتطلب في بيانات الطلاب
                        if prerequisite not in students_df.columns:
                            prereq_satisfied = False
                        else:
                            prereq_status = student[prerequisite]
                            if isinstance(prereq_status, str):
                                prereq_status = prereq_status.strip()
                            # يعتبر المتطلب مستوفى إذا كانت حالته ضمن passed_statuses
                            prereq_satisfied = prereq_status in passed_statuses
                    
                    if not prereq_satisfied:
                        continue
                    
                    # التحقق من عدم تجاوز مجموع الساعات الحد الأقصى (20 ساعة)
                    if total_hours + course_hours <= max_hours:
                        schedule.append(course_code)
                        total_hours += course_hours
                        summary[course_code] = summary.get(course_code, 0) + 1
                
                student_schedules[student_id] = schedule
            
            return student_schedules, summary
        
        # توليد الجداول الدراسية والملخص
        max_hours = st.number_input("أدخل الحد الأقصى للساعات لكل طالب", min_value=1, value=20, step=1)

        if st.button("ولد الجدول"):
            student_schedules, summary = generate_student_schedule(courses_df, students_df, max_hours)
            
            st.header("الجدول الدراسي للفصل القادم لكل طالب")
            # for sid, sched in student_schedules.items():
            #     if sched:
            #         st.markdown(f"**الطالب {sid}:** " + ", ".join(sched))
            #     else:
            #         st.markdown(f"**الطالب {sid}:** لا توجد مقررات متاحة (أو لا تحقق شروط المتطلب السابق)")
            
            
            # تحويل student_schedules إلى DataFrame لعرضه كمخطط Seaborn (Heatmap)
            # سنقوم بإنشاء مصفوفة حيث تمثل الصفوف رقم الطالب والأعمدة تمثل المقررات.
            # إذا كان المقرر موجودًا في جدول الطالب نضع القيمة 1 وإلا 0.
# إنشاء جدول من متغير student_schedules بحيث يكون لكل طالب صف مع أعمدة المقررات
# حساب الحد الأقصى لعدد المقررات المقترحة لأي طالب (لإنشاء أعمدة ثابتة)
            max_courses = max(len(sched) for sched in student_schedules.values())
            
            # بناء قائمة من الصفوف: كل صف يبدأ برقم الطالب ثم المقررات المتاحة، مع تعبئة فراغات إذا كانت أقل من max_courses
            table_data = []
            for student_id, courses in student_schedules.items():
                row = [student_id] + courses + [""] * (max_courses - len(courses))
                table_data.append(row)
            
            # تعريف أسماء الأعمدة: العمود الأول "Student ID" ثم "Course 1", "Course 2", ...
            columns = ["Student ID"] + [f"Course {i+1}" for i in range(max_courses)]
            table_df = pd.DataFrame(table_data, columns=columns)
            
            # إنشاء مجموعة من المقررات الفريدة من جدول الطلاب
            unique_courses = sorted({course for courses in student_schedules.values() for course in courses if course != ""})
            
            # تعريف لوحة ألوان (يمكنك تعديل الألوان أو إضافة المزيد منها)
            color_palette = ['#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#CCFFFF', '#FFCCFF', '#E0E0E0', '#FFDAB9', '#D8BFD8', '#F0E68C']
            course_color_mapping = {course: color_palette[i % len(color_palette)] for i, course in enumerate(unique_courses)}
            
            # دالة لتلوين الخلية بناءً على قيمة المقرر (في الأعمدة من "Course 1" فصاعداً)
            def highlight_course(val):
                if val in course_color_mapping:
                    return f'background-color: {course_color_mapping[val]};'
                else:
                    return ''
            
            # تطبيق التلوين على أعمدة المقررات (باستثناء عمود "Student ID")
            styled_table = table_df.style.applymap(highlight_course, subset=table_df.columns[1:])
            
            # عرض الجدول داخل Streamlit باستخدام st.markdown مع تحويل النتيجة إلى HTML
            st.header("الجدول الدراسي المقترح لكل طالب مع ألوان المقررات")
            st.markdown(styled_table.to_html(), unsafe_allow_html=True)


            st.header("ملخص المواد وعدد الطلاب المحتمل في كل مادة")
            summary_df = pd.DataFrame(list(summary.items()), columns=['CourseCode', 'Number of Students'])
            st.dataframe(summary_df)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملفات: {e}")
