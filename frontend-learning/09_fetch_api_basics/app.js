function mockFetchStudents() {
  // 실제 네트워크 대신 Promise 를 써서 "조금 기다렸다가 데이터가 오는 모습"을 흉내 냅니다.
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { name: "민수", score: 92 },
        { name: "지우", score: 85 },
        { name: "서연", score: 100 },
      ]);
    }, 300);
  });
}

async function lesson1RenderStudents() {
  const app = document.createElement("main");
  app.style.padding = "24px";
  app.innerHTML = `
    <h1>fetch API 교과서 예제</h1>
    <p id="status">데이터를 불러오는 중...</p>
    <ul id="studentList"></ul>
  `;
  document.body.appendChild(app);

  const status = document.getElementById("status");
  const studentList = document.getElementById("studentList");
  const students = await mockFetchStudents();

  status.textContent = "데이터 불러오기 완료";
  for (const student of students) {
    const li = document.createElement("li");
    li.textContent = `${student.name} - ${student.score}점`;
    studentList.appendChild(li);
  }
}

lesson1RenderStudents();
