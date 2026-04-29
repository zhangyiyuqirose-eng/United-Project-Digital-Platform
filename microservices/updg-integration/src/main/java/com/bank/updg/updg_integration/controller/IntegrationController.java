package com.bank.updg.updg_integration.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_integration.service.DevOpsAdapter;
import com.bank.updg.updg_integration.service.FinanceAdapter;
import com.bank.updg.updg_integration.service.HrAdapter;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/integration")
@RequiredArgsConstructor
public class IntegrationController {

    private final HrAdapter hrAdapter;
    private final FinanceAdapter financeAdapter;
    private final DevOpsAdapter devOpsAdapter;

    @GetMapping("/hr/employee/{employeeId}")
    public ApiResponse getEmployeeInfo(@PathVariable String employeeId) {
        return ApiResponse.success(hrAdapter.getEmployeeInfo(employeeId));
    }

    @PostMapping("/hr/sync-org")
    public ApiResponse syncOrg() {
        hrAdapter.syncOrgStructure();
        return ApiResponse.success("同步请求已发送");
    }

    @PostMapping("/finance/settlement")
    public ApiResponse pushSettlement(@RequestBody Map<String, Object> body) {
        String projectId = (String) body.get("projectId");
        BigDecimal amount = new BigDecimal(body.get("amount").toString());
        financeAdapter.pushSettlement(projectId, amount);
        return ApiResponse.success("结算推送已发送");
    }

    @GetMapping("/finance/payment/{settlementId}")
    public ApiResponse queryPaymentStatus(@PathVariable String settlementId) {
        return ApiResponse.success(financeAdapter.queryPaymentStatus(settlementId));
    }

    @GetMapping("/devops/build/{projectId}")
    public ApiResponse getBuildStatus(@PathVariable String projectId) {
        return ApiResponse.success(devOpsAdapter.getBuildStatus(projectId));
    }

    @GetMapping("/devops/test/{projectId}")
    public ApiResponse getTestResults(@PathVariable String projectId) {
        return ApiResponse.success(devOpsAdapter.getTestResults(projectId));
    }
}
