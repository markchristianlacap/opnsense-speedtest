<?php

/*
 * Copyright (C) 2021 Miha Kralj
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

namespace OPNsense\Speedtest\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;

/**
 * Class ServiceController
 * @package OPNsense\Speedtest\Api
 */
class ServiceController extends ApiControllerBase
{
    /**
     * Get speedtest version
     * @return string
     */
    public function versionAction()
    {
        return (new Backend())->configdRun("speedtest version");
    }

    /**
     * Get list of available speedtest servers
     * @return string
     */
    public function serverlistAction()
    {
        return (new Backend())->configdRun("speedtest serverlist");
    }

    /**
     * Run speedtest with optional server ID
     * @param int $serverid Server ID (0 for auto-select)
     * @return string
     */
    public function runAction($serverid = 0)
    {
        return (new Backend())->configdpRun("speedtest run", [$serverid]);
    }

    /**
     * Show speedtest statistics
     * @return string
     */
    public function showstatAction()
    {
        return (new Backend())->configdRun("speedtest showstat");
    }

    /**
     * Show speedtest log
     * @return string
     */
    public function showlogAction()
    {
        return (new Backend())->configdRun("speedtest showlog");
    }

    /**
     * Delete speedtest log
     * @return string
     */
    public function deletelogAction()
    {
        return (new Backend())->configdRun("speedtest deletelog");
    }

    /**
     * Install HTTP-based speedtest (speedtest-cli)
     * @return string
     */
    public function installhttpAction()
    {
        return (new Backend())->configdRun("speedtest install-http");
    }

    /**
     * Install socket-based speedtest (Ookla binary)
     * @return string
     */
    public function installsocketAction()
    {
        return (new Backend())->configdRun("speedtest install-socket");
    }
}
