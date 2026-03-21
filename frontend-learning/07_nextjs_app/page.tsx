type LunchCard = {
  title: string;
  detail: string;
};

function buildLessons(): LunchCard[] {
  return [
    {
      title: "레슨 1. page.tsx 는 곧 하나의 화면",
      detail: "app 폴더의 파일 구조가 URL 구조가 되는 점이 Next.js 의 첫 핵심입니다.",
    },
    {
      title: "레슨 2. 서버 컴포넌트는 필요한 데이터를 먼저 준비하고 렌더링할 수 있다",
      detail: "아직 브라우저에 도착하기 전 단계에서 준비되는 화면이라고 생각하면 쉽습니다.",
    },
    {
      title: "레슨 3. 작은 카드 컴포넌트를 나누면 화면 읽기가 쉬워진다",
      detail: "레고 조각을 나누듯, 반복되는 화면 조각은 함수로 분리합니다.",
    },
  ];
}

function LessonCard({ title, detail }: LunchCard) {
  return (
    <article
      style={{
        padding: 20,
        borderRadius: 16,
        background: "white",
        boxShadow: "0 10px 24px rgba(15, 23, 42, 0.08)",
      }}
    >
      <h2>{title}</h2>
      <p>{detail}</p>
    </article>
  );
}

export default function Page() {
  const lessons = buildLessons();

  return (
    <main
      style={{
        padding: 24,
        minHeight: "100vh",
        background: "linear-gradient(180deg, #fef3c7 0%, #fff7ed 100%)",
        display: "grid",
        gap: 16,
      }}
    >
      <h1>Next.js 페이지 교과서 예제</h1>
      {lessons.map((lesson) => (
        <LessonCard key={lesson.title} {...lesson} />
      ))}
    </main>
  );
}
