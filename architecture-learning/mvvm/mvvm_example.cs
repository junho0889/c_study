using System;
using System.ComponentModel;

namespace ArchitectureLearning.Mvvm
{
    /*
      MVVM은 View가 ViewModel의 속성에 "묶여(binding)" 있다고 상상하면 이해가 쉽습니다.

      비유:
      - ViewModel = 전광판 뒤쪽의 전선 묶음
      - View = 전광판 화면
      전선 값이 바뀌면 화면 글자가 자동으로 바뀌는 느낌입니다.

      이 파일에서는 콘솔 프로그램이라 진짜 XAML 바인딩은 없지만,
      PropertyChanged 이벤트를 직접 출력해서
      "어떤 속성이 바뀌었다고 화면에 알려 주는지"를 눈으로 보게 만듭니다.
    */
    public class StudentModel
    {
        public string Name { get; set; }
        public int Score { get; set; }
        public int StudyMinutes { get; set; }

        public StudentModel(string name, int score, int studyMinutes)
        {
            Name = name;
            Score = score;
            StudyMinutes = studyMinutes;
        }
    }

    public class StudentViewModel : INotifyPropertyChanged
    {
        private readonly StudentModel _model;

        public StudentViewModel(StudentModel model)
        {
            _model = model;
        }

        public string Name => _model.Name;
        public int Score => _model.Score;
        public int StudyMinutes => _model.StudyMinutes;
        public string ResultText => _model.Score >= 70 ? "통과" : "복습 필요";

        public string Summary =>
            $"{_model.Name} 학생은 {_model.Score}점이고, 오늘 {_model.StudyMinutes}분 공부했습니다.";

        public string Advice =>
            _model.Score >= 90
                ? "아주 잘하고 있습니다. 어려운 문제에 도전해 보세요."
                : _model.Score >= 70
                    ? "기본은 잡혔습니다. 틀린 문제만 다시 보면 됩니다."
                    : "아직 헷갈리는 부분이 많으니 쉬운 문제부터 다시 풀어 보세요.";

        public event PropertyChangedEventHandler? PropertyChanged;

        public void AddStudyMinutes(int extraMinutes)
        {
            _model.StudyMinutes += extraMinutes;
            RaiseForScreenRefresh();
        }

        public void ApplyRetestScore(int newScore)
        {
            _model.Score = newScore;
            RaiseForScreenRefresh();
        }

        private void RaiseForScreenRefresh()
        {
            /*
              화면은 Score만 쓰는 것이 아닙니다.
              Summary, Advice, ResultText도 같이 바뀔 수 있습니다.
              그래서 관련된 속성 이름을 모두 알려 줍니다.

              자주 하는 실수:
              - Score만 바꿔 놓고 PropertyChanged("Score")만 보내는 것
              그러면 Summary, Advice를 묶어 둔 화면은 갱신되지 않을 수 있습니다.
            */
            OnPropertyChanged(nameof(Score));
            OnPropertyChanged(nameof(StudyMinutes));
            OnPropertyChanged(nameof(ResultText));
            OnPropertyChanged(nameof(Summary));
            OnPropertyChanged(nameof(Advice));
        }

        private void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
