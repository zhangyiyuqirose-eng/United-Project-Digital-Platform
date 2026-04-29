package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.ContractMapper;
import com.bank.updg.updg_business.model.entity.Contract;
import com.bank.updg.updg_business.service.ContractService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ContractServiceImpl extends ServiceImpl<ContractMapper, Contract>
        implements ContractService {

    @Override
    public Contract createContract(Contract contractData) {
        if (contractData.getContractId() == null || contractData.getContractId().isEmpty()) {
            contractData.setContractId(UUID.randomUUID().toString());
        }
        if (contractData.getContractCode() == null || contractData.getContractCode().isEmpty()) {
            contractData.setContractCode("CT-" + System.currentTimeMillis());
        }
        if (contractData.getCurrency() == null) {
            contractData.setCurrency("CNY");
        }
        if (contractData.getStatus() == null) {
            contractData.setStatus("DRAFT");
        }
        if (contractData.getReminderDays() == null) {
            contractData.setReminderDays(30);
        }
        save(contractData);
        return contractData;
    }

    @Override
    public void updateContract(String contractId, Map<String, Object> data) {
        Contract contract = getById(contractId);
        if (contract == null) {
            throw new RuntimeException("Contract not found: " + contractId);
        }
        if (data.containsKey("contractName")) {
            contract.setContractName((String) data.get("contractName"));
        }
        if (data.containsKey("contractType")) {
            contract.setContractType((String) data.get("contractType"));
        }
        if (data.containsKey("partyA")) {
            contract.setPartyA((String) data.get("partyA"));
        }
        if (data.containsKey("partyB")) {
            contract.setPartyB((String) data.get("partyB"));
        }
        if (data.containsKey("totalAmount")) {
            contract.setTotalAmount((java.math.BigDecimal) data.get("totalAmount"));
        }
        if (data.containsKey("signDate")) {
            contract.setSignDate((String) data.get("signDate"));
        }
        if (data.containsKey("startDate")) {
            contract.setStartDate((String) data.get("startDate"));
        }
        if (data.containsKey("endDate")) {
            contract.setEndDate((String) data.get("endDate"));
        }
        if (data.containsKey("reminderDays")) {
            contract.setReminderDays((Integer) data.get("reminderDays"));
        }
        updateById(contract);
    }

    @Override
    public Contract getContract(String contractId) {
        return getById(contractId);
    }

    @Override
    public Page<Contract> listContracts(String projectId, String type, String status, int page, int size) {
        Page<Contract> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Contract> wrapper = new LambdaQueryWrapper<Contract>()
                .orderByDesc(Contract::getCreateTime);
        if (projectId != null) {
            wrapper.eq(Contract::getProjectId, projectId);
        }
        if (type != null) {
            wrapper.eq(Contract::getContractType, type);
        }
        if (status != null) {
            wrapper.eq(Contract::getStatus, status);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public List<Contract> getExpiringContracts(int days) {
        // Simplified: fetch all effective contracts and filter in memory
        // In production, use a date comparison query
        List<Contract> contracts = list(new LambdaQueryWrapper<Contract>()
                .eq(Contract::getStatus, "EFFECTIVE")
                .isNotNull(Contract::getEndDate));
        // Filter contracts expiring within N days
        java.time.LocalDate now = java.time.LocalDate.now();
        java.time.LocalDate threshold = now.plusDays(days);
        return contracts.stream()
                .filter(c -> {
                    try {
                        java.time.LocalDate end = java.time.LocalDate.parse(c.getEndDate());
                        return !end.isBefore(now) && !end.isAfter(threshold);
                    } catch (Exception e) {
                        return false;
                    }
                })
                .toList();
    }

    @Override
    public void archiveContract(String contractId) {
        Contract contract = getById(contractId);
        if (contract == null) {
            throw new RuntimeException("Contract not found: " + contractId);
        }
        contract.setStatus("ARCHIVED");
        updateById(contract);
    }

    @Override
    public void terminateContract(String contractId, String reason) {
        Contract contract = getById(contractId);
        if (contract == null) {
            throw new RuntimeException("Contract not found: " + contractId);
        }
        contract.setStatus("TERMINATED");
        updateById(contract);
    }
}
