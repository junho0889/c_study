using System;

namespace ArchitectureLearning.Mvp
{
    /*
      MVP에서는 Presenter가 "설명 문장 만들기"까지 더 적극적으로 맡습니다.

      비유:
      - Model = 재료
      - View = 접시
      - Presenter = 요리사

      접시는 요리를 만들지 않습니다.
      요리사가 재료를 보고 음식을 완성해서 접시에 담아 줍니다.
      그래서 View는 아주 단순해지고, Presenter가 화면용 문장을 책임집니다.
    */
    public class StudentModel
    {
        public string Name { get; private set; }
        public int Score { get; private set; }
        public int MissedHomeworkCount { get; private set; }

        public StudentModel(string name, int score, int missedHomeworkCount)
        {
            Name = name;
            Score = score;
            MissedHomeworkCount = missedHomeworkCount;
        }

        public void AddRetestScore(int extraScore)
        {
            Score = Math.Min(100, Score + extraScore);
        }
    }

    public interface IStudentView
    {
        void ShowTitle(string title);
        void ShowStudentCard(string summary);
        void ShowHint(string message);
        void ShowBlankLine();
    }

    /*
      Presenter는 Model의 숫자를 보고
      "지금은 복습이 필요해요", "숙제를 2개 밀렸어요" 같은
      화면용 문장으로 가공합니다.

      자주 하는 실수:
      - View 안에서 if(score < 70) { ... } 를 여러 번 쓰는 것
      이렇게 되면 같은 규칙이 화면마다 복사됩니다.
    */
    public class StudentPresenter
    {
        private readonly StudentModel _model;
        private readonly IStudentView _view;

        public StudentPresenter(StudentModel model, IStudentView view)
        {
            _model = model;
            _view = view;
        }

        public void PresentStudentCard()
        {
            string summary =
                $"이름: {_model.Name}\n" +
                $"점수: {_model.Score}\n" +
                $"밀린 숙제 수: {_model.MissedHomeworkCount}";

            _view.ShowStudentCard(summary);
            _view.ShowHint(BuildAdviceText());
        }

        public void ApplyRetestAndRefresh(int extraScore)
        {
            _model.AddRetestScore(extraScore);
            _view.ShowHint($"재시험 점수 {extraScore}점을 반영했습니다.");
            PresentStudentCard();
        }

        private string BuildAdviceText()
        {
            if (_model.Score < 70)
            {
                return "70점 미만이라서 복습 스티커를 붙여 주세요.";
            }

            if (_model.MissedHomeworkCount >= 2)
            {
                return "점수는 괜찮지만 숙제를 밀렸으니 제출 계획부터 세워야 합니다.";
            }

            return "점수와 숙제 상태가 안정적입니다. 다음 문제를 풀어도 됩니다.";
        }
    }
}
