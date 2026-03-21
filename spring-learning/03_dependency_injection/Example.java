interface AlarmSender {
    String send(String message);
}

class SmsAlarmSender implements AlarmSender {
    @Override
    public String send(String message) {
        return "SMS 전송: " + message;
    }
}

class StudentAlarmService {
    private final AlarmSender alarmSender;

    public StudentAlarmService(AlarmSender alarmSender) {
        this.alarmSender = alarmSender;
    }

    public String notifyScore(String studentName, int score) {
        String message = studentName + " 학생 점수는 " + score + "점입니다.";
        return alarmSender.send(message);
    }
}

public class Example {
    public static void lesson1ConstructorInjection() {
        System.out.println("[레슨 1] 의존성 주입은 필요한 부품을 밖에서 꽂아 넣는 방식입니다.");
        System.out.println();

        StudentAlarmService service = new StudentAlarmService(new SmsAlarmSender());
        System.out.println("  " + service.notifyScore("서연", 100));
        System.out.println();
    }

    public static void main(String[] args) {
        lesson1ConstructorInjection();
    }
}
