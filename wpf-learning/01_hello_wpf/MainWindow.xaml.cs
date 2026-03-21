using System.Windows;

namespace LessonWpf
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            RunInitialLessons();
        }

        private void RunInitialLessons()
        {
            Lesson1WindowLoadsFirst();
            Lesson2CodeBehindUpdatesTheScreen();
        }

        private void Lesson1WindowLoadsFirst()
        {
            /*
              생성자는 창이 만들어질 때 가장 먼저 실행됩니다.
              가게 문을 열자마자 안내판을 세우는 것처럼,
              첫 화면에 보여 줄 기본 문장을 여기서 넣을 수 있습니다.
            */
            MessageText.Text = "창이 열리면 생성자가 먼저 실행되어 첫 문장을 준비합니다.";
        }

        private void Lesson2CodeBehindUpdatesTheScreen()
        {
            HintText.Text =
                "code-behind는 XAML에 있는 이름표(MessageText, HintText)를 찾아 " +
                "실제 글자를 바꾸는 역할을 합니다.";
        }

        private void ShowMessageButton_Click(object sender, RoutedEventArgs e)
        {
            Lesson3HandleButtonClick();
        }

        private void Lesson3HandleButtonClick()
        {
            MessageText.Text = "버튼 클릭 이벤트가 C# 메서드에 연결되었습니다.";

            HintText.Text =
                "실사용 예시: 저장 버튼을 누르면 저장 메서드가 실행되고, " +
                "로그인 버튼을 누르면 로그인 메서드가 실행됩니다. " +
                "즉, XAML은 '어디에 무엇이 있는지', code-behind는 '누르면 무엇을 하는지'를 맡습니다.";
        }
    }
}
