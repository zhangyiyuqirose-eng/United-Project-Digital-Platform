package com.bank.updg.common.flow;

import lombok.RequiredArgsConstructor;
import org.flowable.engine.RuntimeService;
import org.flowable.engine.TaskService;
import org.flowable.engine.runtime.ProcessInstance;
import org.flowable.task.api.Task;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * Flowable 流程通用操作封装
 */
@Component
@RequiredArgsConstructor
public class FlowableService {

    private final RuntimeService runtimeService;
    private final TaskService taskService;

    /**
     * 启动流程实例
     *
     * @param processDefinitionKey 流程定义 Key
     * @param businessKey          业务 ID
     * @param variables            流程变量
     */
    public ProcessInstance startProcess(String processDefinitionKey, String businessKey,
                                        Map<String, Object> variables) {
        return runtimeService.startProcessInstanceByKey(processDefinitionKey, businessKey, variables);
    }

    /**
     * 完成审批任务
     *
     * @param taskId    任务 ID
     * @param variables 审批变量（如 approved=true, comment="同意"）
     */
    public void completeTask(String taskId, Map<String, Object> variables) {
        taskService.complete(taskId, variables);
    }

    /**
     * 驳回任务
     *
     * @param taskId   任务 ID
     * @param comment  驳回意见
     */
    public void rejectTask(String taskId, String comment) {
        taskService.addComment(taskId, null, comment);
        taskService.complete(taskId);
    }

    /**
     * 查询用户待办任务
     *
     * @param assignee 审批人 ID
     */
    public java.util.List<Task> getTasksByAssignee(String assignee) {
        return taskService.createTaskQuery().taskAssignee(assignee).list();
    }

    /**
     * 根据业务 ID 查询流程实例
     */
    public ProcessInstance getProcessByBusinessKey(String businessKey) {
        return runtimeService.createProcessInstanceQuery()
                .processInstanceBusinessKey(businessKey)
                .singleResult();
    }
}
