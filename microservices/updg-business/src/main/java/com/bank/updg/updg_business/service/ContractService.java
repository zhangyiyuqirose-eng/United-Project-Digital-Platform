package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.Contract;

import java.util.List;
import java.util.Map;

public interface ContractService extends IService<Contract> {

    Contract createContract(Contract contractData);

    void updateContract(String contractId, Map<String, Object> data);

    Contract getContract(String contractId);

    Page<Contract> listContracts(String projectId, String type, String status, int page, int size);

    List<Contract> getExpiringContracts(int days);

    void archiveContract(String contractId);

    void terminateContract(String contractId, String reason);
}
